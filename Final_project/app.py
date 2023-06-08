from flask import Flask, render_template, request
from pandas import read_csv
import random
import pickle
app = Flask(__name__)
app = Flask(__name__, template_folder='HtmlForms')
@app.route('/')
def index():
    fake_data = read_csv('fake_user_data.csv')
    netflix_data = read_csv('new_netflix_datas.csv')
    
    #sorted alphabetically
    fake_data = sorted(set(fake_data['Username'].values))
    netflix_data = sorted(netflix_data['title'].values)

    return render_template('index.html',usernames = fake_data, movies = netflix_data)

def get_user_genres(user,k_means_model):
    shows = k_means_model[k_means_model['Username'] == user]
    #separates genres with commas and determines what type of movie the user watches
    genres = list(set(genre for genres in shows['genres'].str.split(',') for genre in genres))
    return genres


@app.route('/k_means_recommend', methods=['POST'])
def k_means_recommend():
    user = request.form.get('username')
    #load model
    with open('Models\k_means_model.pkl', 'rb') as file:
        model = pickle.load(file)
    
    user_data = model[model['Username'] == user]
    cluster = model['clusters'].values[0]
    shows = set(user_data['Watched Title'].values)
    #In order to make a suggestion, it must be in the same cluster with a different username and the same movie type.
    user_clusters = model[(model['clusters'] == cluster) &
                                 (model['Username'] != user) &
                                 (model['genres'].isin(get_user_genres(user,model)))]
    show_clusters = user_clusters['Watched Title'].values
    recommendations = [show for show in show_clusters if show not in shows]
    random.shuffle(recommendations)
    recommend = recommendations[:5] 
    return render_template('k_means.html', username = user, recommendations = recommend)


@app.route('/association_recommend', methods=['POST'])
def association_recommend():
    movie = request.form.get('movie')
    #I use Double \\ becuse single \ gives error.
    with open('Models\\association_model.pkl', 'rb') as file:
        model = pickle.load(file)
    
    # Find matching association rules for the user's selected show and sort by confidence
    matching_rules = model[model['antecedents'] == frozenset([movie])]
    matching_rules = matching_rules.sort_values('confidence', ascending=False)

    # Get recommended shows from the association rules
    recommended_shows = [item for sublist in matching_rules['consequents'].apply(list) for item in sublist]
    recommended_shows = recommended_shows[:4]
    return render_template('association.html', movie = movie, recommendations = recommended_shows)

if __name__ == "__main__":
    app.run(debug=True)