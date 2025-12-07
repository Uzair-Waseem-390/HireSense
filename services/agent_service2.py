from agents import Runner, set_tracing_disabled, Agent, AsyncOpenAI, OpenAIChatCompletionsModel
from core import config
from schemas import agent_schemas

set_tracing_disabled(True)



gemini_api_key = config.settings.gemini_api_key
gemini_base_url = config.settings.base_url

gemini_clint = AsyncOpenAI(api_key=gemini_api_key, base_url=gemini_base_url)

gemini_model1 = OpenAIChatCompletionsModel(openai_client=gemini_clint, model="gemini-2.5-flash")

gemini_model2 = OpenAIChatCompletionsModel(openai_client=gemini_clint, model="gemini-2.5-flash-lite")

# extracted_text: str
class AgentService:
    def analyze_resume_with_agent(self, extracted_text: str) -> agent_schemas.ResumeData:
        resume_analysis_agent = Agent(
            name="Resume Analysis Agent",
            model=gemini_model1,
            instructions="""
                You are an expert **Data Extraction Agent** specializing in parsing professional documents like resumes, CVs, and biography snippets.

        Your core mission is to analyze the provided text content, which contains information about a person's professional background, and strictly extract the following four pieces of information:
        1.  **Skills**
        2.  **Experience** (including total years and specific positions)
        3.  **Education**
        4.  **Professional Summary**

        ### Extraction Rules and Constraints:
        * **Skills:** Identify technical, professional, or specialized skills. The resulting array must contain a **maximum of 15 skills**.
        * **Experience - total_years:** Calculate the total number of professional years listed. If you cannot determine the number from the text, use $\text{null}$ or $\text{0}$.
        * **Experience - positions:** For each position, extract the **title**, **company**, and the **years** (as a string, e.g., "2018 - 2023" or "2 years").
        * **Education:** List the main qualifications, degrees, or certifications.
        * **Summary:** Generate a concise professional summary of the person, strictly limited to **2 to 3 sentences**. The summary must be synthesized from the provided text.

        Your output **must strictly adhere** to the provided JSON Schema for reliable programmatic parsing. Do not include any conversational filler, explanation, or markdown formatting other than the required JSON object.
                """,
                output_type = agent_schemas.ResumeData,
            )


        res = Runner.run_sync(
            starting_agent= resume_analysis_agent,
            input=extracted_text,
            # """John Doe has over 5 years of experience in software development. 
            # He worked at TechCorp as a Senior Developer from 2018 to 2023, 
            # focusing on backend systems and cloud infrastructure. Prior to that, 
            # he was a Junior Developer at WebSolutions from 2015 to 2018. 
            # John holds a Bachelor's degree in Computer Science from State University and is proficient in Python,
            # Java, and AWS. He is passionate about building scalable applications and improving system performance.""",
        )
        return res.final_output 
        # print(res.final_output)

    # candidate_data_json = analyze_resume_with_agent.res.final_output.model_dump_json(indent=2)
    def analyze_job_fit_with_agent(self, job_description: str, resume_data: agent_schemas.ResumeData) -> agent_schemas.JobMatchData:
        job_matcher_agent = Agent(
            name="Job Matcher Agent",
            model=gemini_model1,
            instructions="""
                You are an expert **Job Matcher and Assessment Agent**. Your task is to analyze a job description (JD) and a candidate's structured resume data to determine the fitness of the candidate for the role.

                ### Input Data:
                1. **Job Description (JD):** A block of unstructured text outlining the role requirements.
                2. **Candidate Data:** A structured JSON object (derived from a resume) containing Skills, Experience, Education, and Summary.

                ### Calculation Rules and Constraints:
                * **Fit Score:** Calculate a score from 0 to 100 based on the overlap between required skills/experience in the JD and those listed in the candidate data. The most critical requirements in the JD should carry the most weight.
                * **Strengths:** Identify 3 to 5 specific matches (skills, experience keywords, or qualifications) that strongly benefit the candidate.
                * **Missing Skills:** Identify 3 to 5 technical or professional skills that are explicitly mentioned or strongly implied as necessary in the JD but are NOT present in the candidate's skills list.
                * **Recommendations:** Provide 2 to 3 concise, actionable suggestions for the candidate to close the identified gaps or improve their profile alignment with the JD.

                Your output **must strictly adhere** to the provided JSON Schema (JobMatchData) for reliable programmatic parsing. Do not include any conversational filler or explanation.
            """,
            output_type=agent_schemas.JobMatchData,
        )
        # Prepare input properly
        candidate_data_json = resume_data.model_dump_json(indent=2)

        res2 = Runner.run_sync(
            starting_agent= job_matcher_agent,
            input=
            f""""job_description": {job_description},
            "candidate_data": {candidate_data_json}""",
            # f"""
            #     "job_description": We are seeking a Software Engineer with 5+ years of experience in backend development, 
            #     proficiency in Python and AWS, and a strong understanding of cloud infrastructure. 
            #     Experience with Docker and Kubernetes is a plus. The ideal candidate will have a Bachelor's degree in Computer Science 
            #     or a related field and excellent problem-solving skills.,
            #     "candidate_data": """,
            #     # {self.analyze_resume_with_agent().model_dump_json(indent=2)}
        )

        return res2.final_output

        # print(final_output := res2.final_output)

# print(AgentService().analyze_resume_with_agent())
# print(AgentService().analyze_job_fit_with_agent())