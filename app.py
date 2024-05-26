from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
from flask_cors import CORS
from PIL import Image
import numpy as np

app = Flask(__name__)
CORS(app)

model = load_model('smile_model.h5')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    try:
        # Чтение содержимого файла и преобразование в изображение
        image = Image.open(file)
        image = image.resize((256, 256))  # Измените размер изображения на необходимый вашей модели
        image = np.array(image)
        if image.shape[-1] == 4:  # Проверка на альфа-канал и его удаление
            image = image[..., :3]
        image = np.expand_dims(image, axis=0)  # Добавление батч измерения
        image = image / 255.0  # Нормализация изображения
        print(f"Processed image shape: {image.shape}")
        
        # Прогнозирование с использованием модели
        prediction = model.predict(image)[0][0]  # Предполагается, что модель возвращает значение в диапазоне от 0 до 1
        print(f"Prediction: {prediction}")
        
        # Преобразование предсказаний в метки
        predicted_label = 'радость' if prediction < 0.5 else 'грусть'
        response = {
            'prediction': predicted_label
        }
        return jsonify(response)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
