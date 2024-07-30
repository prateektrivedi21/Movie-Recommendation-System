import pickle
import streamlit as st
import requests
import pandas as pd
import base64
from datetime import datetime

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=31b4d2af5d76969f2c5824937e980e38&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path')
    if (poster_path):
        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    else:
        full_path = "https://via.placeholder.com/500x750?text=No+Image"
    return full_path


def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=31b4d2af5d76969f2c5824937e980e38&language=en-US"
    data = requests.get(url).json()
    return data


def fetch_movie_cast(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key=31b4d2af5d76969f2c5824937e980e38&language=en-US"
    data = requests.get(url).json()
    cast = data['cast']
    crew = data['crew']
    cast_details = []
    for member in cast[:10]:  # Limit to top 10 cast members
        cast_details.append({
            'name': member['name'],
            'character': member['character'],  # Include character role
            'profile_path': member['profile_path'],
            'id': member['id']  # Add cast member ID
        })

    director = next((member['name'] for member in crew if member['job'] == 'Director'), 'N/A')
    return cast_details, director


def fetch_cast_details(cast_id):
    url = f"https://api.themoviedb.org/3/person/{cast_id}?api_key=31b4d2af5d76969f2c5824937e980e38&language=en-US"
    data = requests.get(url).json()
    biography = data.get('biography', 'N/A')
    if len(biography) > 750:
        biography = biography[:747] + '...'
    return {
        'name': data['name'],
        'birthday': data.get('birthday', 'N/A'),
        'place_of_birth': data.get('place_of_birth', 'N/A'),
        'biography': biography,
        'profile_path': data.get('profile_path', None)
    }


def cast_member_html(cast):
    return f"""
    <div class='cast-member'>
        <img src='{cast["profile_path"]}' class='cast-photo'/>
        <div class='cast-details'>
            <h3 class='cast-text' title='{cast["name"]}'>
                {cast["name"]}
            </h3>
        </div>
    </div>
    """


def add_custom_css():
    with open("styles/style.css") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)


def add_bg_from_local(image_file):
    with open(image_file, "rb") as image:
        encoded_string = base64.b64encode(image.read()).decode()
    st.markdown(
        f"""
         <style>
         .stApp {{
             background-image: url("data:image/png;base64,{encoded_string}");
             background-size: cover;
             background-position: center;
             background-repeat: no-repeat;
             background-attachment: fixed;
         }}
         </style>
         """,
        unsafe_allow_html=True
    )

# Adding Font Awesome CSS for icons
st.markdown(
    """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    """,
    unsafe_allow_html=True
)

add_custom_css()
add_bg_from_local('images/14.jpeg')

# Adding the main header at the top of the page
st.markdown('<h1 class="header">Movie Recommender System</h1>', unsafe_allow_html=True)
movies_dict = pickle.load(open('assets/movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))
movie_list = movies['title'].values

selected_movie = st.selectbox(
    "",
    movie_list
)


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]

    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_movie_ids = []
    recommended_movie_release_dates = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        movie_details = fetch_movie_details(movie_id)  # Fetch movie details to get the release date
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_ids.append(movie_id)
        recommended_movie_release_dates.append(movie_details['release_date'])  # Get the release date
    return recommended_movie_names, recommended_movie_posters, recommended_movie_ids, recommended_movie_release_dates


if st.button('Recommend'):
    add_bg_from_local('images/image.jpg')  # Change the background image upon recommendation
    st.markdown(
        """
        <style>
        .header {
            color:transparent;
        }
        .stSelectbox > div > div {
            width: 50%;
            background-color: transparent;
            color: white;
            border: 2px solid #ffffff;
            border-radius: 5px;
        }
        .recommended-movie:hover img{ 
            transform: scale(1.2);
            transition: transform 0.2s;
        }
        .cast-text:hover{
            color: #D3D3D3;
        }
        .cast-photo:hover{
            transform: scale(1.2);
            transition: transform 0.2s;
            -webkit-box-shadow: 0px 1px 15px 4px rgba(250,250,250,1);
            -moz-box-shadow: 0px 1px 15px 4px rgba(250,250,250,1);
            box-shadow: 0px 1px 15px 4px rgba(250,250,250,1); 
        }
        .t-header:hover, .subheader:hover, .recommend:hover, p:hover, .expander-content:hover h3{
            color : #FFAE42;
        }

        @media (max-width: 768px) {
            .recommended-movie, .cast-member, .selected-movie-poster{
                margin: 10px;
            }
            .cast-photo, .movie-poster {
                max-width: 100px.
                height: auto.
            }
        }

        @media (max-width: 480px) {
            .stSelectbox > div > div {
                width: 90%;
            }
            .movie_font_details {
                font-size: 16px;
            }
            .subheader, #top-name, .expander-content {
                font-size: 26px;
            }
            .recommend{
                font-size: 18px;
            }
            .cast-info div {
                max-width: 100%.
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    movie_id = movies[movies['title'] == selected_movie].iloc[0].movie_id
    movie_details = fetch_movie_details(movie_id)
    cast_details, director = fetch_movie_cast(movie_id)

    st.markdown(f"<h1 class='movie_font_details' id='top-name'>{movie_details['title']}</h1>",
                unsafe_allow_html=True)
    col1, col2 = st.columns([1, 4], gap="medium")
    with col1:
        st.markdown(
            f"""
            <a href="https://www.themoviedb.org/movie/{movie_id}" target="_blank">
                <img src='{fetch_poster(movie_id)}' class='selected-movie-poster'/>
            </a>
            """,
            unsafe_allow_html=True
        )
    with col2:
        genres = ", ".join([genre['name'] for genre in movie_details['genres']])
        rating_formatted = f"{movie_details['vote_average']}/10 ({movie_details['vote_count']} votes)"
        release_date_formatted = datetime.strptime(movie_details['release_date'], '%Y-%m-%d').strftime('%b %d, %Y')

        st.markdown(f"<p class='movie_font_details'><b>Title:</b> {movie_details['title']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='movie_font_details'><b>Overview:</b><p id='overview'>{movie_details['overview']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='movie_font_details'><b>Release Date:</b> {release_date_formatted}</p>",unsafe_allow_html=True)
        st.markdown(f"<p class='movie_font_details'><b>Director:</b> {director}</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='movie_font_details'><b>Runtime:</b> {movie_details['runtime']} minutes</p>",unsafe_allow_html=True)
        st.markdown(f"<p class='movie_font_details'><b>Genre:</b> {genres}</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='movie_font_details'><b>Rating:</b> {rating_formatted}</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='movie_font_details'><b>Status:</b> {movie_details['status']}</p>",unsafe_allow_html=True)

    st.markdown('<h1 class="subheader">Top Cast of the Movie</h1>', unsafe_allow_html=True)
    st.markdown('<p class="recommend">(Expand to uncover hidden gems about your favorite stars!)</p>',unsafe_allow_html=True)
    num_col = 5
    cast_cols = st.columns(num_col)
    placeholder_image_url = "https://via.placeholder.com/500x750?text=No+Image"
    for idx, cast in enumerate(cast_details):  # Access cast details correctly
        with cast_cols[idx % num_col]:
            profile_image_url = placeholder_image_url
            if cast['profile_path']:
                profile_image_url = "https://image.tmdb.org/t/p/w500/" + cast['profile_path']
            st.markdown(
                cast_member_html({
                    "profile_path": profile_image_url,
                    "name": cast['name'],
                    "character": cast['character']
                }),
                unsafe_allow_html=True
            )
            with st.expander(cast['character']):
                cast_info = fetch_cast_details(cast['id'])
                st.markdown(
                    f"""
                    <div class='cast-info expander-content'>
                        <div>
                            <h3>{cast_info['name']}</h3>
                            <p><b>Birthday:</b> {cast_info['birthday']}</p>
                            <p><b>Place of Birth:</b> {cast_info['place_of_birth']}</p>
                            <p><b>Biography:</b> {cast_info['biography']}</p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.markdown('<h1 class="subheader">Top Recommended Movies for a Cozy Night In</h1>', unsafe_allow_html=True)
    st.markdown('<p class="recommend">(Discover more by clicking on your selected movie!)</p>', unsafe_allow_html=True)
    recommended_movie_names, recommended_movie_posters, recommended_movie_ids, recommended_movie_release_dates = recommend(selected_movie)

    num_recommendations = len(recommended_movie_names)
    num_columns = 5  # Number of columns in the layout
    cols = st.columns(num_columns)
    for idx in range(num_recommendations):
        with cols[idx % num_columns]:
            st.markdown(
                f"""
                <div class='recommended-movie'>
                    <a href="https://www.themoviedb.org/movie/{recommended_movie_ids[idx]}" target="_blank">
                        <img src='{recommended_movie_posters[idx]}' class='movie-poster'/>
                    </a>
                </div>
                <div class='scrollable-text' title='{recommended_movie_names[idx]}'>
                 <h5 class='movie-text'>{recommended_movie_names[idx]}<br>({datetime.strptime(recommended_movie_release_dates[idx], '%Y-%m-%d').strftime('%b %d, %Y')})</h5>
                </div>
                """,
                unsafe_allow_html=True
            )

# Added copyright notice as a footer
st.markdown(
    """
    <footer class='footer'>
        <p style='font-family: "Netflix Sans", "Helvetica Neue", Helvetica, Arial, sans-serif; color: white;'>© 2024 Created by Prateek Trivedi <a href="https://github.com/prateektrivedi21"><i class="fab fa-github"></i></a>. All rights reserved.</p>
    </footer>
    """,
    unsafe_allow_html=True
)
