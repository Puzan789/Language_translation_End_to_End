
# END TO END LANGUAGE TRANSLATION PIPELINE
### **Project Structure**

```bash
├── config/
│   └── config.yaml     
├── params/
│   └── params.yaml
├── src/
│   ├── translator/
│   │   ├── components/
│   │   │   ├── __init__.py
│   │   │   ├── dataingestion.py
│   │   │   ├── datatransform.py
│   │   │   ├── datavalidation.py
│   │   │   ├── modeltrain.py
│   │   │   └── modeltransform.py
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   └── configuration.py
│   │   ├── constants/
│   │   │   ├── __init__.py
│   │   ├── entity/
│   │   │   ├── __init__.py
│   │   ├── inference/
│   │   │   ├── __init__.py
│   │   ├── logging/
│   │   │   ├── __init__.py
│   │   ├── logs/
│   │   ├── model/
│   │   │   ├── __init__.py
│   │   │   └── mytranslatormodel.py
│   │   ├── pipeline/
│   │   │   ├── __init__.py
│   │   │   ├── stage_01_dataingestion.py
│   │   │   ├── stage_02_datavalidation.py
│   │   │   ├── stage_03_datatransform.py
│   │   │   ├── stage_04_modeltrain.py
│   │   │   └── stage_05_deployment.py
│   │   ├── utils/
│   │       ├── __init__.py
│   │       └── common.py
│
├── translatorapi/
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── users.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── userschemas.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── userservice.py
│   ├── dependencies.py
│   ├── main.py
├── requirements.txt
├── Readme.md
├── setup.py
├── template.py
```

## Project Features Checklist

- ✅ **End-to-End Transformer Implementation**: End-to-end transformer model implemented from scratch in a training notebook on Kaggle.
- ✅ **Pipeline Creation for Transformer Components**: Created pipelines for each component of the transformer model (data ingestion, Validation, Transformation, Training and evaluate,Translate).
- ✅ **User Login/Logout Functionality**: Integrated user authentication and logout functionality using FastAPI.
- ⬜ **API Key Generation**: Logged-in users will receive an API key, which they can use to integrate with their applications.
- ⬜ **UI Design**: Designed a user interface (UI) where users can authenticate, generate API keys, and use real-time language translation.





### 1. Clone the Repository

You can clone this repository by running the following command:

```bash
git clone https://github.com/Puzan789/Language_translation_End_to_End
```

### 2. Install Dependencies

After cloning, navigate to the project directory and install the required dependencies using `requirements.txt`:

```bash 
pip install -r requirements.txt
```

### 3. Update the Configuration

Make sure to update your `config.yaml` file with the correct `SOURCE_URL`. This file can be found in the `config/` directory:

```yaml
SOURCE_URL: <your_data_source_url> #EXAMPLE:https://github.com/Puzan789/Datas/raw/refs/heads/main/translatordata.zip
```

**Note**:  
Your dataset must contain labeled source and target data and should be in a zip file format.

### 4. Adjust Parameters

Before running the pipeline, ensure that all necessary parameters are set in `params/params.yaml`. 

### 5. Run the Training Pipeline

Once your data and parameters are properly set, the entire training process is handled by the pipeline. Run the pipeline to start training:

```bash
python main.py  # Run individual stages
# Or you can run all stages sequentially as needed
```

### 6. FastAPI Translator API

To run the API, navigate to the `translatorapi/` folder and start the FastAPI application:

```bash
cd translatorapi
uvicorn fastapi dev main.py
```

This will launch the API, which includes endpoints for user authentication and  language translation.

