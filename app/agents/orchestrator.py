import json
import re
from sqlalchemy.ext.asyncio import AsyncSession
import autogen
from app.agents.specialized_agents import create_trust_agent, create_matchmaking_agent, create_summary_agent
from app.agents.registered_tools import verify_user_trust, find_potential_mentors, save_session_summary

class MatchmakingOrchestrator:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.llm_config = {
            "model": "llama3.2:1b",
            "api_key": "not-needed", 
            "base_url": "http://127.0.0.1:4000" 
        }

    # Tool wrapper methods remain unchanged
    async def _verify_user_trust_tool(self, user_id: int) -> str:
        return await verify_user_trust(user_id, self.db)

    async def _find_potential_mentors_tool(self, skill_name: str) -> str:
        return await find_potential_mentors(skill_name, self.db)

    async def _save_session_summary_tool(self, session_id: int, summary_text: str) -> str:
        return await save_session_summary(session_id, summary_text, self.db)

    async def initiate_matchmaking_flow(self, user_id: int, skill_name: str, request_details: str) -> dict:
        # === STEP 1: VERIFICATION CONVERSATION ===
        print("--- Kicking off Step 1: Verification ---")
        trust_agent = create_trust_agent(llm_config=self.llm_config)
        verification_proxy = autogen.UserProxyAgent(
            name="VerificationProxy",
            human_input_mode="NEVER",
            code_execution_config=False,
        )
        verification_proxy.register_function(
            function_map={"verify_user_trust": self._verify_user_trust_tool}
        )

        verification_prompt = f"Verify the trustworthiness of user with ID {user_id}. Use the tool."
        await verification_proxy.a_initiate_chat(trust_agent, message=verification_prompt)
        
        verification_result = verification_proxy.last_message(trust_agent)["content"]
        
        if "UNTRUSTWORTHY" in verification_result:
            print(f"--- Verification FAILED. Reason: {verification_result} ---")
            return {"status": "FAILED", "reason": f"User is untrustworthy: {verification_result}"}
        
        if "VERIFIED" not in verification_result:
             print(f"--- Verification FAILED. Unexpected response: {verification_result} ---")
             return {"status": "FAILED", "reason": f"Verification failed with an unexpected agent response."}

        print("--- Verification SUCCEEDED ---")

        # === STEP 2: MATCHMAKING CONVERSATION ===
        print("--- Kicking off Step 2: Matchmaking ---")
        matchmaking_agent = create_matchmaking_agent(llm_config=self.llm_config)
        matchmaking_proxy = autogen.UserProxyAgent(
            name="MatchmakingProxy",
            human_input_mode="NEVER",
            code_execution_config=False,
        )
        matchmaking_proxy.register_function(
            function_map={"find_potential_mentors": self._find_potential_mentors_tool}
        )
        
        matchmaking_prompt = (
            f"The user is verified. Now find a mentor for the skill '{skill_name}'. "
            f"The user's request details are: '{request_details}'. "
            "First, use the tool to find mentors. Then, analyze the list and respond with the JSON for the best mentor."
        )
        await matchmaking_proxy.a_initiate_chat(matchmaking_agent, message=matchmaking_prompt)
        
        # Extract the final result from the matchmaking agent
        final_message = matchmaking_proxy.last_message(matchmaking_agent)["content"]
        
        print(f"--- Matchmaking agent final response: {final_message} ---")
        if "best_mentor_id" in final_message:
            try:
                json_str_match = re.search(r'{.*}', final_message)
                if json_str_match:
                    result_json = json.loads(json_str_match.group())
                    print(f"--- Matchmaking SUCCEEDED. Mentor ID: {result_json['best_mentor_id']} ---")
                    return {"status": "SUCCESS", "mentor_id": result_json["best_mentor_id"]}
            except (json.JSONDecodeError, KeyError):
                pass # Fall through to failure case if JSON is invalid

        print("--- Matchmaking FAILED. Could not extract mentor ID. ---")
        return {"status": "FAILED", "reason": "Matchmaking agent did not return a valid mentor ID.", "last_message": final_message}

    # The summary agent flow is already a simple two-agent chat, so it doesn't need this refactor.
    async def facilitate_session_summary(self, session_id: int, transcript: str) -> dict:
        summary_agent = create_summary_agent(llm_config=self.llm_config)
        summary_proxy = autogen.UserProxyAgent(
            name="SummaryProxy", human_input_mode="NEVER",
            is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
            code_execution_config=False,
        )
        summary_proxy.register_function(function_map={"save_session_summary": self._save_session_summary_tool})
        initial_prompt = (
            f"The mentorship session with ID {session_id} has concluded.\n"
            f"Transcript:\n---\n{transcript}\n---\n"
            "Generate a concise summary and use the `save_session_summary` tool to save it. "
            "After saving, confirm and TERMINATE."
        )
        await summary_proxy.a_initiate_chat(summary_agent, message=initial_prompt)
        last_message = summary_proxy.last_message(summary_agent)["content"]
        if "SUCCESS" in last_message or "saved" in last_message:
            return {"status": "SUCCESS", "message": "Summary saved."}
        else:
            return {"status": "FAILED", "reason": "Agent failed to save summary.", "last_message": last_message}