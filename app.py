# this is a language translator

import os
from openai import AsyncOpenAI
os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = "1"
from agents import Agent,function_tool,OpenAIChatCompletionsModel, Runner,ModelSettings,model_settings
from dotenv import load_dotenv
import gradio as gr


load_dotenv()
openai_api_key = os.getenv("API_KEY")

if openai_api_key:
    print("API KEY DETECTED")
else:
    print("API KEY NOT FOUND")

client = AsyncOpenAI(api_key=openai_api_key,base_url="https://openrouter.ai/api/v1")
 
# this is for the text translation
Text_Model = OpenAIChatCompletionsModel(openai_client=client,model="gpt-4o-mini")

# this is for the audio translation
#Audio_Model = OpenAIChatCompletionsModel(openai_client=client,model="gpt-4o-mini-audio")

system_message = ("""
You are a High-Fidelity Translation Agent. Your goal is to bridge linguistic gaps while maintaining the exact tone, nuance, and cultural context of the source text.

Core Directives
Contextual Accuracy: Do not translate word-for-word. Prioritize the intent and idiomatic equivalent in the target language.

Tone Preservation: If the source is formal/academic, keep the translation professional. If it is slang-heavy or casual, reflect that energy.

Cultural Adaptation (Localization): Adjust units of measurement, date formats, and localized references (e.g., currency or metaphors) unless specified otherwise.

Ambiguity Handling: If a sentence is structurally ambiguous, provide the most likely translation and list 1-2 alternatives in a brief "Notes" section.

Output Format
For every translation request, provide the following structure:

Translation: The polished, final text and audio.

Key Terms: A brief table for technical or industry-specific jargon used.

Nuance Notes: (Optional) Only if there is a cultural specific or double meaning the user should be aware of.

Constraints
No "Hallucinations": If a word is untranslatable, keep the original term in italics and provide a brief definition.

Neutrality: Maintain the bias/perspective of the original author without adding your own commentary.
""")

# this  instance of the Agent uses the text model
text_speaker = Agent(
    name="OpenDialect",
    instructions=system_message,
    model=Text_Model,
    model_settings=ModelSettings(
        modalities=["text","audio"],
        voice= "alloy",
        output_audio_format="wav"
    )

    
    
)
# this instance of the Agent uses the audio model
# i did this because i couldn't find my way around gpt-4o-mini-audio preview, error wrong model id
audio_speaker = Agent(
    name="OpenDialect",
    instructions=system_message,
    model=Text_Model,
    model_settings=ModelSettings(
        modalities=["text","audio"],
        voice= "alloy",
        output_audio_format="wav"
    )  
)

# this function is for text translation
async def  text_translator(in_put,out_put):

    out_put = await Runner.run(text_speaker,in_put)
    
    return out_put.final_output

# this function is for audio input  translation
async def audio_translator(audio_in):

    output = await Runner.run(audio_speaker,input=audio_in)
    result = output.final_output.audio.transcript
    text = output.final_output.content
    audio = output.final_output.audio.data


    return text,audio

# this creates the container
with gr.Blocks(title="Open Dialect") as app:
    #gr.HTML("<h3> Open Dialect </h3>")
    gr.Markdown("# Open Dialect")
    gr.Markdown("### Language Detection and Translation Agent")
    
# the audio  input box
    with gr.Row():
        # input audio
        audio_in = gr.Audio(label="Speak Here",sources=["microphone"],type="filepath")

# the row for the input and output boxes
    with gr.Row():

        # detected and text to be translated text input box
        first_box = gr.Textbox(label="Detected Language",
                               show_label=True,
                               interactive=True,
                               )
        # translated text output box
        second_box = gr.Textbox(label="Translation")

# this the submit button, it takes the text translator function  and executes the inputted text 
    with gr.Row():
        submit_btn = gr.Button(value="Submit",variant="primary")
        submit_btn.click(
            fn=text_translator,
            inputs=[first_box],
            outputs=[second_box]
        )

        # this outputs the translated audio output, it is not visible in the main screen
    audio_out = gr.Audio(label="Translation Voice",autoplay=True,visible=False)

# this is like a gradio function, it automaticaly executes once the audio is stopped, in this case its takes a function audio #translator and matches automatically matches it to the input and output and executes it. this block of code is used to execute
#the input audio and it executes onces the stop button is pressed
    audio_in.stop_recording(
        fn=audio_translator,
        inputs=audio_in,
        outputs=[second_box,audio_out]
    )
# this launches the application
app.launch(share=True)




































def main():
    print("Hello from opendialect!")


if __name__ == "__main__":
    main()
