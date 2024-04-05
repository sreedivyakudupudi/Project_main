from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import trail
from trail import db
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, File, UploadFile, Form
from PIL import Image, ImageOps
import tensorflow as tf
import numpy as np
import io
app = FastAPI()

corn_model = tf.keras.models.load_model(r"C:\food\pythonProject\corn.h5")
tomato_model = tf.keras.models.load_model(r"C:\food\pythonProject\tomato.h5")
potato_model = tf.keras.models.load_model(r"C:\food\pythonProject\potato_model.h5")
paddy_model = tf.keras.models.load_model(r"C:\food\pythonProject\rice_model.h5")
corn_diseases = ['Blight', 'Common Rust', 'Gray Leaf Spot', 'Healthy']
tomato_diseases = ['Bacterial spot',
 'Early blight',
 'Late blight',
 'Leaf Mold',
 'Septoria leaf spot',
 'Spider mites Two spotted spider mite',
 'Target Spot',
 'Yellow Leaf Curl Virus',
 'mosaic virus',
 'healthy']


potato_disease = ['Early blight', 'Late blight', 'healthy']
paddy_disease = ['Bacterial leaf blight', 'Brown spot', 'Healthy', 'Leaf smut']
   
def predict_disease(image_data,model):
    size=(256,256)
    img = image_data.resize(size)
    img_array = np.array(img)
    reshape = img_array[np.newaxis, ...]  
    pred = model.predict(reshape)
    return pred


@app.post("/")
async def handle_request(request: Request):
    # try:
    #     payload = await request.json()
    #     intent = payload['queryResult']['intent']['displayName']
    #     parameters = payload['queryResult']['parameters']
    #     output_contexts = payload['queryResult']['outputContexts']
    #     context = output_contexts[0]
    #     params = context['parameters']
   
    #     if 'cropname' in params:
    #         crop_name = params['cropname']
    #     elif 'CropName' in params:
    #         crop_name = params['CropName']
    #     else:
    # # Handle the case where neither key is present
    #         crop_name = None
    #     if 'diseasename' in params:
    #         disease_name = params['diseasename']
    #     elif 'DiseaseName' in params:
    #         disease_name = params['DiseaseName']
    #     else:
    #             # Handle the case where neither key is present
    #         disease_name = None

    #         # Check if either 'informationtype' or 'informationType' is present
    #     if 'informationtype' in parameters:
    #         information_type = parameters['informationtype']
    #     elif 'informationType' in parameters:
    #         information_type = parameters['informationType']
    #     else:
    #             # Handle the case where neither key is present
    #         information_type = None
    #     return handle_user_information_query(information_type, crop_name, disease_name)
    try:
        payload = await request.json()
        intent = payload['queryResult']['intent']['displayName']
        parameters = payload['queryResult']['parameters']
        output_contexts = payload['queryResult']['outputContexts']
        context = output_contexts[0]
        params = context['parameters']

        crop_name = params.get('cropname') or params.get('CropName')
        disease_name = params.get('diseasename') or params.get('DiseaseName')

        information_type = parameters.get('informationtype') or parameters.get('informationType')
        if crop_name is None or disease_name is None:
            # Look for the "ongoingchat" context only when crop_name or disease_name is None
            ongoing_chat_context = next((context for context in output_contexts if context['name'].endswith('/ongoingchat')), None)
            if ongoing_chat_context:
                params = ongoing_chat_context['parameters']
                crop_name = crop_name or params.get('CropName')
                disease_name = disease_name or params.get('DiseaseName')
            else:
                return {"error": "Crop name or disease name is None"}

        return handle_user_information_query(information_type, crop_name, disease_name)



    except KeyError as e:
        return {"error": f"KeyError: {e}"}

    except Exception as e:
        return {"error": str(e)}

def handle_user_information_query(information_type: str, crop: str, disease: str):
    if information_type is None:
        return {"fulfillmentText": "Please specify the information type (remedies, precautions, products)."}

    # Based on the information type, fetch and return relevant information from the database
    if information_type == "remedies":
        remedies = db.get_remedies(crop, disease)
        return {"fulfillmentText": "Here are some remedies: " + remedies}
    elif information_type == "precautions":
        precautions = db.get_precautions(crop, disease)
        return {"fulfillmentText": "Here are some precautions: " + precautions}
    elif information_type == "fertilisers":
        products = db.get_products(crop, disease)
        return {"fulfillmentText": "Here are some products: " + products}
    elif information_type == "cause":
        print("hi")
        ans = db.get_cause(crop, disease)
        print(ans)
        return {"fulfillmentText": ""+ ans}

    else:
        return {"fulfillmentText": "I'm sorry, I didn't understand your request."}

# Endpoint to handle image upload and predict disease
@app.post("/predict")
async def predict_crop_disease(image_file: UploadFile = File(...), crop_name: str = Form(...)):
    contents = await image_file.read()
    image = Image.open(io.BytesIO(contents))
    print(crop_name)
    # Select the appropriate model based on crop name
    if crop_name.lower() == "corn":
        model = corn_model
        labels = corn_diseases  
    elif crop_name.lower() == "tomato":
        model = tomato_model
        labels = tomato_diseases  
    elif crop_name.lower() == "potato":
        model = potato_model
        labels = potato_disease 
    elif crop_name.lower() == "paddy":
        model = paddy_model
        labels = paddy_disease 
    else:
        return {"error": "Unsupported crop name"}
    
    # Predict disease
    pred = predict_disease(image, model)
    print(np.argmax(pred))
    predicted_disease = labels[np.argmax(pred)]
    print(predicted_disease)
    if(predicted_disease.lower() == "healthy"):
        result = "<b>Don't Worry!! your crop is healthy</b>"
        return {"predicted_disease": predicted_disease, "result": result, "remedies":"", "precaution":""}
  
    else:
        remedies = "<b>Here are some remedies:</b><br><br>"
        remedies = remedies+db.get_remedies(crop_name,predicted_disease)
        prec = "<br><br><b>Here are some Precautions:</b><br><br>"
        prec = prec +db.get_precautions(crop_name,predicted_disease)
        result = "<br><b>Here are some products:</b><br>"
        result = result +db.get_products(crop_name,predicted_disease)   
        prec = prec.replace("\n","<br>")
        result = result.replace("\n","<br>")
        remedies = remedies.replace("\n","<br>")
        # print(prec)
    # Additional processing and response formatting can be added here
    return {"predicted_disease": predicted_disease, "result": result, "remedies":remedies, "precaution":prec}
   
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("static/home.html", "r") as file:
        html_content = file.read()
    return html_content

