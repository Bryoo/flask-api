from flask.views import MethodView
from flask import make_response, request, jsonify
from app.models import User
from app.auth import auth_blueprint


class RegistrationView(MethodView):
    def post(self):
        """ tests post """
        email = request.json.get('email', '')
        user = User.query.filter_by(email=email).first()
        if not user:
            try:
                post_user = request.json
                # Register the user
                email = post_user['email']
                password = post_user['password']
                username = post_user['username']

                user = User(email=email, password=password, username=username)
                user.save()

                response = {
                    'message': 'Successfully registered.'
                }
                # return a response notifying the user that they registered successfully
                result = jsonify(response)
                result.status_code = 201
                return result

            except Exception as error:
                # Error on creating a user
                response = {
                    'message': str(error)
                }
                return jsonify(response)
        else:
            # Duplicate user
            response = {
                'message': 'User already exists'
            }

            return jsonify(response)


class LoginView(MethodView):
    """Handles logging in and access based token"""
    def post(self):
        # handles the post request for the user login
        email = request.json.get('email', '')
        password = request.json.get('password', '')
        try:
            user = User.query.filter_by(email=email).first()
            # authenticate found user
            if user and user.password_is_valid(password):
                access_token = user.generate_token(user.id)
                response = {
                    'message': 'You logged in successfully.',
                    'access_token': access_token.decode()
                }
                return make_response(jsonify(response)), 200

            else:
                # user doesn't exist
                response = {
                    'message': 'Invalid email or password, Please try again'
                }
                return make_response(jsonify(response)), 401
        except Exception as e:
            # Create a response containing an string error message
            response = {
                'message': str(e)
            }
            # Return a server error using the HTTP Error Code 500 (Internal Server Error)
            return make_response(jsonify(response)), 500


registration_view = RegistrationView.as_view('register_view')
login_view = LoginView.as_view('login_view')

auth_blueprint.add_url_rule(
    '/auth/register',
    view_func=registration_view,
    methods=['POST'])

auth_blueprint.add_url_rule(
    '/auth/login',
    view_func=login_view,
    methods=['POST'])
