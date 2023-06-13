#Using Affinda for resume parsing - 50 free documents on free trial
#Documentation: https://api.affinda.com/docs#post-/v2/resumes
#Request free trial: https://www.affinda.com/resume-parser

from pathlib import Path
import os
from affinda import AffindaAPI, TokenCredential
from affinda.models import WorkspaceCreate, CollectionCreate

class ResumeParser:
    def __init__(self):
        self.client = AffindaAPI(credential=TokenCredential(token='194b914ec110d0684408bbe223871a0894237004'))

    def parse_pdf(self, pdf_file_path):
        #

        # First get the organisation, by default your first one will have free credits
        my_organisation = self.client.get_all_organizations()[0]
        workspace = self.client.get_all_workspaces(my_organisation.identifier)[0]
        collection = self.client.get_all_collections(workspace.identifier)[0]

        # # And within that organisation, create a workspace, for example for Recruitment:
        # workspace_body = WorkspaceCreate(
        #     organization=my_organisation.identifier,
        #     name="My Workspace",
        # )
        # recruitment_workspace = self.client.create_workspace(body=workspace_body)

        # # Finally, create a collection that will contain our uploaded documents, for example resumes, by selecting the
        # # appropriate extractor
        # collection_body = CollectionCreate(
        #     name="Resumes", workspace=recruitment_workspace.identifier, extractor="resume"
        # )
        # resume_collection = self.client.create_collection(collection_body)

        # Create resume with file
        file_pth = Path(pdf_file_path)

        with open(file_pth, "rb") as f:
            resume = self.client.create_document(file=f, collection=collection.identifier)

        return resume.as_dict()

    def format_resume(self, resume_dict):
        #Takes the output from Affinda and formats to a format that we need
        parsed = {}
        parsed['name'] = resume_dict['data']['name']['raw']
        parsed['total_years_experience'] = resume_dict['data']['total_years_experience']
        parsed['education'] = []
        for e in resume_dict['data']['education']:
            education_dict = {}
            education_dict['organization'] = e.get('organization', '')
            education_dict['degree'] = e['accreditation']['input_str']
            parsed['education'].append(education_dict)

        parsed['work'] = []
        for w in resume_dict['data']['work_experience']:
            work_dict = {}
            work_dict['company'] = w.get('organization', '')
            work_dict['title'] = w.get('job_title', '')
            work_dict['job_description'] = w.get('job_description', '')
            parsed['work'].append(work_dict)

        parsed['skills'] = []
        for s in resume_dict['data']['skills']:
            parsed['skills'].append(s['name'])

        return parsed
    
    def construct_embed_string(self, pdf_file_path):
        formatted = self.format_resume(self.parse_pdf(pdf_file_path))
        embed_string = ''
        embed_string += f"The candidate's name is {formatted['name']}, and he has a total of {formatted['total_years_experience']} years of experience \n"
        for e in formatted['education']:
            embed_string += f"The candidate has a degree in {e['degree']} from {e.get('organization', '')}\n"
        
        embed_string += '\n\n'
        for w in formatted['work']:
            embed_string += "The candidate worked at "
            embed_string += f"{w['company']} as a {w['title']}. Responsibilities included \n"
            for jr in w['job_description'].split('\n'):
                embed_string += jr + '\n'
            embed_string += '\n \n'
        
        embed_string += '\n\n'
        embed_string += 'The candidate is skilled in the following \n'
        for s in formatted['skills']:
            embed_string += s + '\n'
        
        return embed_string

if __name__=='__main__':
    rs = ResumeParser()
    es = rs.construct_embed_string("./data/SampleResume3.pdf")
    print(es)