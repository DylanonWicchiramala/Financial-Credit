import gradio as gr
from chatbot_multiagent import AgentBot

Bot = AgentBot(keep_chat_history=False, return_reference=False, verbose=False)


# def chat(message:str, history):
#     print(message)
#     return submitUserMessage(message)


# def slow_echo_chat(message, history):
#     answer = submitUserMessage(message)
#     for i in range(len(answer)):
#         time.sleep(0.01)
#         yield answer[: i+1]
        
        
with gr.Blocks() as demo:
    chatbot = gr.Chatbot(height=600)
    msg = gr.Textbox()
    clear = gr.ClearButton([msg, chatbot])

    def respond(message, chat_history):
        bot_message = Bot.submit_user_message_with_debug_command(message)
        chat_history.append((message, bot_message))
        return "", chat_history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    

demo.launch()
        
# gr.ChatInterface(chat).launch()

# interface = gr.ChatInterface(chat)
# interface.launch()