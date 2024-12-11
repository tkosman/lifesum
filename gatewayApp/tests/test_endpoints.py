# """
# This file contains the tests for the endpoints in the app.
# """
# import json

# from cryptography.hazmat.primitives import serialization

# def test_register_user(public_key, test_client):
#     """ Test the register endpoint."""
#     payload = {
#         "user_id": "test_user",
#         "public_key": public_key
#     }
#     _, response = test_client.post("/register", content=json.dumps(payload))
#     assert response.status == 201
#     assert response.json == {"message": "User registered successfully."}

#     _, response = test_client.post("/register", content=json.dumps(payload))
#     assert response.status == 400
#     assert response.json["error"] == "User ID already exists."


# def test_generate_challenge(test_client):
#     """ Test the challenge generation endpoint."""
#     payload = {
#         "user_id": "test_user"
#     }
#     _, response = test_client.post("/challenge", content=json.dumps(payload))
#     assert response.status == 200
#     assert "challenge" in response.json
#     assert response.json["user_id"] == "test_user"

# def test_protected_endpoint_without_token(test_client):
#     """ Test no access the protected endpoint without a token."""
#     _, response = test_client.get("/protected")
#     assert response.status == 401
#     assert response.json["error"] == "You are unauthorized."

# def test_full_authentication_flow(private_key, public_key, sign_challenge_func_fixture,decrypt_challenge_func_fixture , test_client):
#     """
#     Test the full authentication flow.
#     1. Register a user.
#     2. Generate a challenge.
#     3. Sign the challenge.
#     4. Authenticate the user.
#     5. Access the protected endpoint.
#     """
#     payload = {
#         "user_id": "auth_user",
#         "public_key": public_key
#     }
#     _, response = test_client.post("/register", content=json.dumps(payload))
#     assert response.status == 201

#     payload = {"user_id": "auth_user"}
#     _, response = test_client.post("/challenge", content=json.dumps(payload))
#     assert response.status == 200
#     challenge_hex = response.json["challenge"]
#     challenge_bytes = bytes.fromhex(challenge_hex)


#     private_key_obj = serialization.load_pem_private_key(private_key.encode(), password=None)
#     decrypted_challenge_bytes = decrypt_challenge_func_fixture(private_key_obj, challenge_bytes)
#     signed_challenge = sign_challenge_func_fixture(private_key_obj, decrypted_challenge_bytes)

#     auth_payload = {
#         "user_id": "auth_user",
#         "signed_challenge": signed_challenge.hex()
#     }
#     _, response = test_client.post("/auth", content=json.dumps(auth_payload))
#     assert response.status == 200
#     assert "access_token" in response.json

#     access_token = response.json["access_token"]
#     headers = {"Authorization": f"Bearer {access_token}"}
#     _, response = test_client.get("/protected", headers=headers)
#     assert response.status == 200
#     assert response.json["message"] == "This is a protected endpoint."
