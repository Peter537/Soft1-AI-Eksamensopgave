# Setup

1. `pip install -r requirements.txt`
2. Create an `.env` file with `API_KEY=<your key>`
3. `streamlit run app.py`

# Env-file

The `MODEL` is the name of the model you want to use.

The `API_KEY` is found by pressing on your profile picture in the top right corner of the Open WebUI interface, then pressing "Settings" (or "Indstillinger" in Danish), and then going to "Account" (or "Profil" in Danish). Here you will find your API key which you can copy and paste into the `.env` file.

The `.env` file should contain the following variables:

```
API_KEY=<your key>
MODEL=<your model>
```

# The knowledge-base system

> TODO: Ret senere i tilfælde af at det virker med api-side knowledge ellers er nedenstående nok det vi får med.

We attempted to build a standalone application based off of our cleaned dataset from part 1 and having the AI loaded and supplied with the database as RAG vector database (knowledge in Open WebUI).

API-side knowledge does not seem to be something explained or presented in their documentation page and it seems to be something you can only truly append using the Open WebUI interface which lead us to applying it in the following way:

## Setting up knowledge for our own AI model for our part 2 use-case

1. Finding knowledge base page: Open up the Open WebUI frontend application (made from their docker script)
   a. Navigate to the workspace tab on the top-left under "New Chat" and "Notes"
   b. Navigate to the "Knowledge" tab and click on the "+" sign at the far right.
2. Creating your own knowledge-base: You are given several inpuits here. Naming your knowledge, appending a prompt to it; the description (its use-case), visibility to the public or private to your internal groups and what groups have access.
   a. We wrote the folloinwg:
   ´´´
   Name: API-P2-Knowledge
   Knowledge Description: Assistance (as instructed by their documentation, this works well for database knowledge)
   Visibility: Public
   Groups: None
   ´´´
3. To append a file to this knowledge you simply click on the plus and "Upload files" and select the file you want

   > In our experience, anything besides xlsx (excel files) takes forever to load and performs very poorly in practice. We have tried csv and JSON which performed poorly [**TODO: This needs to be redone and checked again**] so we opted for xlsx which performed much better and was also something supplied by the user-base in this [Github Thread](https://github.com/open-webui/open-webui/discussions/8813)

4. Assigning the knowledge to the AI model. Navigate away from the "Workspace" tab and return to the "New Chat" so that the profile picture button shows again in the top right and click on it
   a. Navigate to "Admin Panel" -> Settings -> Models
   b. Select the model you would like to use for the project (Note that this will give the general model the knowledge-base but this can easily be removed again)
5. System prompt and knowedge

   In this part we decided to use OpenWebUI for both support prompting the AI and assigning our cleaned dataset to it.
   We do this by entering our support prompts (The 4 T's) [[[**TODO: THIS NEEDS TO BE DONE**]]] after which we attach the knowledge-base to the AI under the "Knowledge" section. Here we select the prior named Knowledge "AI-P2-Knowledge"

   then remember to click "Save & update"

Now we can use the model with knowledge tied to it. You simply query to that same model using the completions-api and that finishes this setup.
