from flask import Flask, render_template, request, redirect, url_for, jsonify
from utils import get_recos, get_previous_movies

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        return redirect(url_for('user', user_id=user_id))
    return render_template('index.html', recommendations=None)


@app.route('/user/<user_id>', methods=['GET', 'POST'])
def user(user_id):
    previous_movies = get_previous_movies(user_id)      
    return render_template('user.html', user_id=user_id, recommendations=previous_movies, previous_page=url_for('index'))
    
    

# ... other Flask app code ...

@app.route('/get_recommendations')
def get_recommendations():
    # Simulate generating recommendations with a DataFrame
    user_id = request.args.get('user_id')
    print('Getting recommendations for user: ', user_id)
    
    recommendations = get_recos(user_id)  # Implement this function to get movie recommendations
    print('Got recommendations for user: ', user_id)
    
    print(recommendations)
    # Convert DataFrame to JSON and return
    recommendations_json = recommendations.to_json(orient='records')
    print(recommendations_json)
    return jsonify(recommendations_json)



if __name__ == '__main__':
    app.run(host='0.0.0.0',port=7000)
