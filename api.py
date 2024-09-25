from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import json
import requests
import os
from chatbot_multiagent import submitUserMessage
import utils
import line_bot
import crm

crm.run_pipelines()

utils.load_env()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_TOKEN")
CHANNEL_SECRET = os.environ.get("LINE_SECRET")
BOT_VERBOSE = int(os.environ['BOT_VERBOSE'])

@app.route('/', methods=['POST', 'GET'])
async def webhook():
    if request.method == 'POST':
        payload = request.json
        # Log the entire payload for debugging
        app.logger.info(f"Received payload: {json.dumps(payload, indent=2)}")
        
        try:
            # Check Event (can be multiple event)
            for event in payload['events']:
                user_id = event["source"]["userId"]
                # Get reply token (reply in 1 min)
                reply_token = event['replyToken']                        
                if event['type'] == 'message':
                    user_message = event["message"]["text"]
                    # Model Invoke
                    response = submitUserMessage(user_message, user_id=user_id, keep_chat_history=True, return_reference=False, verbose=BOT_VERBOSE)
                    response = utils.format_bot_response(response, markdown=False)
                    line_bot.ReplyMessage(reply_token, response)
            
            return request.json, 200
        
        except Exception as e:
            app.logger.error(f"Error: {e}")
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "method not allowed"}), 400
        
        
@app.route('/test', methods=['POST', 'GET'])
def chatbot_test():
    try:
        user_message = request.json.get('message', '')
        
    except Exception as e:
        app.logger.error(f"Error: {e}")
        return jsonify({"error": f"{e}"}), 500

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        response = submitUserMessage(user_message, user_id="test", keep_chat_history=False, return_reference=True, verbose=BOT_VERBOSE)
        response = utils.format_bot_response(response, markdown=False)
        
        if isinstance(response, list):
            response = response[0]
        
        return jsonify({"response": response})

    except Exception as e:
        app.logger.error(f"Error: {e}")
        return jsonify({"error": f"{e}"}), 500
        
        
@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Perform any necessary checks here (e.g., database connection, etc.)
        # For now, we just return a simple success message
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        # If something goes wrong, return an error message
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


# Run the Flask app
if __name__ == '__main__':
    app.run(port=8080, debug=True)