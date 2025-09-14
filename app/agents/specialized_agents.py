from autogen import ConversableAgent
from typing import Dict, Any

def create_trust_agent(llm_config: Dict[str, Any]) -> ConversableAgent:
    """Creates the Trust & Verification Agent."""
    return ConversableAgent(
        name="TrustAndVerificationAgent",
        system_message="""
        You are a Trust and Verification Agent. Your ONLY job is to verify user trustworthiness.
        You MUST use the `verify_user_trust` tool provided to you.
        Based on the tool's output, you will state CLEARLY if the user is 'VERIFIED' or 'UNTRUSTWORTHY'.
        If UNTRUSTWORTHY, state the reason.
        Do not do anything else. Do not find mentors. Do not chat.
        After you give the status, the MatchmakingAgent will take over.
        """,
        llm_config=llm_config,
        human_input_mode="NEVER",
    )

def create_matchmaking_agent(llm_config: Dict[str, Any]) -> ConversableAgent:
    """Creates the Intelligent Matchmaking Agent."""
    return ConversableAgent(
        name="MatchmakingAgent",
        system_message="""
        You are an Intelligent Matchmaking Agent. Your purpose is to find the best mentor.
        You will ONLY act AFTER the TrustAndVerificationAgent has confirmed a user is 'VERIFIED'.
        Your first step is to use the `find_potential_mentors` tool to get a list of mentors.
        After you get the list, your second step is to analyze it and choose the single best mentor ID.
        You MUST then respond with ONLY a JSON object containing the chosen mentor's ID, like this: {"best_mentor_id": 123}.
        Do not add any other text or explanation. Just the JSON. This is your final action.
        """,
        llm_config=llm_config,
        human_input_mode="NEVER",
    )

def create_summary_agent(llm_config: Dict[str, Any]) -> ConversableAgent:
    """Creates the Learning Summary Generation Agent."""
    # This agent is not part of the failing flow, but its prompt is already well-defined.
    return ConversableAgent(
        name="SummaryAgent",
        system_message="""
        You are the Learning Summary Generation Agent.
        You will receive a raw transcript of a mentorship session.
        Your task is to create a concise, insightful, and structured summary.
        The summary should include:
        - Key topics discussed.
        - Core advice given by the mentor.
        - Actionable next steps for the mentee.
        - 2-3 key learning outcomes.
        After generating the summary, use the `save_session_summary` tool to save it.
        Respond with confirmation that the summary has been saved, then TERMINATE.
        """,
        llm_config=llm_config,
        human_input_mode="NEVER",
    )