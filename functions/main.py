from typing import Any
from firebase_functions import db_fn
from firebase_admin import initialize_app, firestore, db
import asyncio

app = initialize_app()

@db_fn.on_value_written(reference=r"/users/{uid}/experience_score", region="us-central1")
def update_leaderboard(event):
    """
    Triggered when a user's experience score is updated.
    """
    new_score = event.data.after
    uid = event.params['uid']

    # Call the asynchronous function
    asyncio.run(process_update(uid, new_score))


async def process_update(uid, new_score) -> Any:
    try:
        # Fetch user details from Firestore
        user_ref = firestore.client().collection('users').document(uid)
        user_doc = user_ref.get()

        if user_doc.exists:
            user_data = user_doc.to_dict()
            firstname = user_data.get('first_name', 'Unknown')
            lastname = user_data.get('last_name', 'Unknown')

            # Check if the user exists in the rankings
            leaderboard_ref = db.reference(f"leaderboard/{new_score}/{uid}")
            existing_score = leaderboard_ref.get()

            if existing_score:
                # Update the rankings in Realtime Database with initials
                leaderboard_ref.update({
                    'initials': f"{firstname[0]}{lastname[0]}"
                })
                print(f"Leaderboard updated for user {uid} with score {new_score}.")
            else:
                # Set the ranking in Realtime Database with initials
                leaderboard_ref.set({
                    'initials': f"{firstname[0]}{lastname[0]}"
                })

                print(f"Leaderboard updated for user {uid} with score {new_score}.")
        else:
            print(f"User {uid} not found in Firestore.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
