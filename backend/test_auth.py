from flask import jsonify

def test_auth_route(app):
    @app.route('/api/test-auth')
    def test_auth():
        from flask_jwt_extended import current_user, jwt_required
        @jwt_required()
        def protected():
            return jsonify({'message': f'Hello, {current_user.username}!'})
        return protected()
