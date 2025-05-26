# Table of Contents

- [Introduction](#1-introduction)
- [Setup](#2-setup)
  - [Settting up the .env file](#21-settting-up-the-env-file)
  - [Setting up OpenWebUI](#22-setting-up-openwebui)
- [Model evaluation](#3-model-evaluation)
  - [Data used](#31-data-used)
  - [Models used](#32-models-used)
  - [Results](#33-results)

# 1. Introduction

The project is about using an already published AI-model and connecting it to a knowledge base that is built from a cleaned dataset from part 1 of the project. The goal is to create a chatbot that can answer user questions about a car dealership and its cars based on the dataset.

We attempted to build a standalone application based off of our cleaned dataset from part 1 and having the AI loaded and supplied with the database as RAG vector database (knowledge in Open WebUI).

API-side knowledge does not seem to be something explained or presented in OpenWebUI's documentation page and it seems to be something you can only truly append using the OpenWebUI interface.

# 2 Setup

1. `pip install -r requirements.txt`

2. Create an `.env` file

> Note: The section [#2.1 Setting up the .env file](README.md/#21-settting-up-the-env-file) describes how to set up the `.env` file.

3. Setup knowledge and system-prompts in OpenWebUI

> Note: The section [#2.2 Setting up OpenWebUI](README.md/#22-setting-up-openwebui) describes how to set up OpenWebUI with the knowledge base and system prompts.

4. Run the app using `streamlit run app.py`

## 2.1 Settting up the .env file

The `.env` file should contain the following variables:

```
API_KEY=<your key>
MODEL=<your model>
```

The `MODEL` is the name of the model you want to use, e.g. `llama3.2:3b`

The `API_KEY` is found by pressing on your profile picture in the top right corner of the Open WebUI interface, then pressing "Settings", and then going to "Account". Here you will find your API key which you can copy and paste into the `.env` file.

## 2.2 Setting up OpenWebUI

1. Finding knowledge base page:

Open up the Open WebUI frontend application

a. Navigate to the "Workspace" tab on the top-left under "New Chat" and "Notes"

b. Navigate to the "Knowledge" tab and click on the "+" sign at the far right.

2. Creating your own knowledge-base:

You are given several inputs here. Naming your knowledge, appending a prompt to it; the description (its use-case), visibility to the public or private to your internal groups and what groups have access.

We wrote the following:

&emsp;**Name:** `API-P2-Knowledge`

&emsp;**Knowledge Description:** `Assistance` (as instructed by their [documentation](https://docs.openwebui.com/tutorials/tips/rag-tutorial/#setup), this works well for database knowledge)

&emsp;**Visibility:** `Public`

&emsp;**Groups:** `None`

3. To append a file to this knowledge you simply click on the plus and "Upload files" and select the file you want. In our case it would be one of the cleaned dataset found in [../data/](../data/).

4. Assigning the knowledge to the AI model.

Navigate away from the "Workspace" tab and return to the "New Chat" so that the profile picture button shows again in the top right and click on it

a. Navigate to "Admin Panel" -> "Settings" -> "Models"

b. Select the model you would like to use for the project (_Note: this will give the general model the knowledge-base but this can easily be removed again_)

5. System prompt and knowledge

We are using OpenWebUI for both system prompting the AI and assigning our cleaned dataset to it.

This is done by entering our [system-prompt.txt](./system-prompt.txt) (3 of the 4 T's, since the 4th T (task) will come from the user input) into the "System Prompt" section in the Model.

Afterwards, we attach the knowledge-base we created earlier to the AI under the "Knowledge" section, where you click on "Select Knowledge" and select the prior named Knowledge "API-P2-Knowledge".

Then remember to click "Save & update" in the bottom of the page to save your changes.

---

Now we can use the model with knowledge tied to it. You simply query to that same model using the completions-API and that finishes this setup.

# 3 Model evaluation

## 3.1 Data used

As we said in the "Setting up OpenWebUI" section, we used the cleaned dataset from part 1 of the project. The datasets are located in the [../data/](../data/) folder, with the following files:

- `dataset_cleaned.csv`: The cleaned dataset from part 1 of the project.
- `dataset_cleaned_sorted.csv`: The cleaned dataset from part 1 of the project, sorted by price.
- `dataset_cleaned_sorted.xlsx`: The cleaned dataset from part 1 of the project, sorted by price in Excel format.
- `dataset_cleaned_sorted.json`: The cleaned dataset from part 1 of the project, sorted by price in JSON format.

## 3.2 Models used

We use these models for the project:

- `llama3.2:3b` (3b parameters, 2 GB)
- `gemma3:4b` (4b parameters, 3.3 GB)
- `deepseek-r1:14b` (14b parameters, 9 GB)

## 3.3 Results

### 3.3.1 Best dataset format

- Json

The JSON format suffered from poor data handling and, despite our modest dataset size, struggled to return meaningful query results. For example, when we asked for the cheapest car it reported values in the $27,000 range even though our actual cheapest entry was $549, indicating that its parsing or indexing of the JSON fragments was fundamentally flawed.

- CSV

The CSV files yielded consistently good responses across all tested models, demonstrating reliable relative comparisons and fast performance. Although not the smallest format at 2.7 MB (vs. 1.6 MB for XLSX), it proved both size- and speed-optimized. It too failed to pinpoint the $549 car, but this appears tied more to vectorization limits than to format interpretation.

- Xlsx

XLSX delivered the smallest file size but exhibited inconsistent performance: it faltered noticeably with DeepSeek-r1 yet worked reasonably well under llama 3.2:3b. Its tendency to report "unable to see data" suggests that, like JSON, the way fragments are handled in XLSX leads to unreliable query coverage.

### 3.3.2 Model

Our experiments reveal that each model fragments and retrieves data in its own distinct way, affecting both accuracy and conversational robustness.

This smaller llama variant exhibited the fastest response times and rarely hallucinated, but its data retrieval was inconsistent. Although it could follow straightforward queries quickly, it frequently failed to locate specific records or returned incomplete results, undermining its reliability for precise information lookup.

Gemma 3 struck a balance between precision and speed: it accurately identified individual datapoints and reported their attributes correctly. However, its context window proved insufficient for extended back-and-forth dialogue. In multi-message exchanges, it struggled to maintain continuity, often dropping earlier requests or losing track of the user's line of inquiry.

DeepSeek R1 outperformed the others for sustained, detailed data exploration. It not only pinpointed target rows and surrounding columns with high accuracy but also sustained longer conversational threads without degradation. Its memory retention enabled more complex, multi-step interactions, making it the most dependable choice for our use cases.

### 3.3.3 Final remarks

Our findings cover that model architecture plays a pivotal role in how data is vectorized and queried. While we initially hypothesized that the vector database (rather than model complexity) would dominate retrieval quality, it became clear that the model itself is ultimately responsible for parsing and interpreting the embedded vectors. Consequently, more capable models yield more accurate results.

However, even our most powerful model (DeepSeek R1 with 14 billion parameters) consistently failed to identify the single cheapest car in our dataset. This suggests that the vectorization process in OpenWebUI is a critical bottleneck: regardless of model strength, the assistant's ability to surface precise records is constrained by how the knowledge base is converted into embeddings. In its current form, it may not be realistic to expect an LLM-driven assistant to fully replace structured database queries.

Moving forward, we plan to explore even larger models with expanded parameter counts to determine whether they can overcome these limitations. Such experiments will demand significantly greater computational resources.
