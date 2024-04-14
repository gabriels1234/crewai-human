import os
import json
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from langchain_groq import ChatGroq
from langchain_community.tools import HumanInputRun

load_dotenv()


def get_input() -> str:
    print(":> ('q' or Ctrl-D to end.)")
    contents = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == "q":
            break
        contents.append(line)
    return "\n".join(contents)


human_tool = HumanInputRun(input_func=get_input)


def get_agent_task_json_repository(key="all"):

    # this could evolve as a backend (file/db) + repository

    life_coach_agent_data_json = """
    {
        "role": "Common sense life-coach",
        "goal": "Uncover the problems of the other people. must ask a question to the human. Must not be too pushy, i.e insist more than once if the human does not want to answer",
        "backstory": "You are a life coach with a strong background in psychology and counseling. You're an active listener, and does not offer advice unless asked. Just Ask questions!"
    }
    """
    # "expected_output": "In a markdown-formatted format. INCLUDE THE CONVERSATION: QUESTION, ANSER, QUESTION, ANSWER. and then your analysis conclussion/advice. What I discovered about the other person's situation: ... Advice as Life Coach: ...",
    # "description": "Make a meaningful conversation with the other person and uncover the problems they are facing",
    task_provide_life_coaching_session_json = """
    {
        "description": "Make a meaningful conversation with the other person and uncover the problems they are facing, in order to produce a report based on the conversation.",
        "expected_output": "Write the above conversation in a nicely markdown-formatted text, including headings, sub-headings, etc, and then give your impressions about the human and advice as a life coach.",
        "output_file": "life_coach_output.md"
    }
    """
    data = {
        "agent_life_coach": life_coach_agent_data_json,
        "task_provide_life_coaching_session": task_provide_life_coaching_session_json,
    }
    if key == "all":
        return data
    return data[key]  # raises KeyError if key is not found


def main():
    repository = get_agent_task_json_repository("all")
    life_coach_agent_args = json.loads(
        repository.get("agent_life_coach", "ERROR. CANNOT CONTINUE WITHOUT AGENT DATA")
    )
    task_provide_life_coaching_session_args = json.loads(
        repository.get(
            "task_provide_life_coaching_session",
            "ERROR. CANNOT CONTINUE WITHOUT TASK DATA",
        )
    )  # could load from a file
    llm_args = get_agent_crew_llm_args("default")
    life_coach_agent_meta_args = {
        "allow_delegation": False,
        "tools": [human_tool],  # most important tool for this agent
        **(llm_args["agent"]),
    }

    life_coach = Agent(
        **life_coach_agent_args,
        **life_coach_agent_meta_args,
    )

    # Create tasks for your agents
    task_provide_life_coaching_session = Task(
        **task_provide_life_coaching_session_args,
        agent=life_coach,
    )
    # Instantiate your crew with a sequential process
    crew = Crew(
        agents=[life_coach],
        tasks=[task_provide_life_coaching_session],
        **(llm_args["crew"]),
        #   verbose=2,  # uncomment for verbose mode
    )

    # Get your crew to work!
    result = crew.kickoff()

    print("######################")
    print(result)


def get_groq_agent_llm_args():
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    groq_model = os.environ.get("GROQ_MODEL_NAME", "mixtral-8x7b-32768")
    groq_llm = ChatGroq(api_key=GROQ_API_KEY, model=groq_model)
    groq_max_iter = 10  # To handle how many iterations the model should run (reduce if it's still insisting on doing it over and over again)

    return {
        "agent": {
            "llm": groq_llm,
            "max_iter": groq_max_iter,
            "max_rpm": 100,
            "verbose": True,
        },
        "crew": {
            "max_rpm": 29,
        },
    }


def get_agent_crew_llm_args(agent_name="default"):
    llm_data = {
        "default": get_groq_agent_llm_args(),
        # Add more llms here
    }
    return llm_data.get(agent_name, get_groq_agent_llm_args())


if __name__ == "__main__":
    main()
