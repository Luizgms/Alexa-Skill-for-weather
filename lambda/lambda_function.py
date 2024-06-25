# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import requests
import boto3

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('41f6a042-d4ad-4354-8c0f-baf578498f2b')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

traducoes_tempo = {
    "Thunderstorm": "Tempestade",
    "Drizzle": "Garoa",
    "Rain": "Chuva",
    "Snow": "Neve",
    "Clear": "Céu Limpo",
    "Clouds": "Nublado",
    "Mist": "Névoa",
    "Smoke": "Fumaça",
    "Haze": "Neblina",
    "Dust": "Poeira",
    "Fog": "Nevoeiro",
    "Sand": "Areia",
    "Ash": "Cinzas",
    "Squall": "Rajada",
    "Tornado": "Tornado"
}

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Bem vindo ao seu app de tempo!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class ClimaCidadeFavoritaIntentHandler(AbstractRequestHandler):
    """Handler para o Intent ClimaCidadeFavoritaIntent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ClimaCidadeFavoritaIntent")(handler_input)

    def handle(self, handler_input):
        try:
            response = table.get_item(Key={'id': handler_input.request_envelope.session.user.user_id})
            item = response.get('Item')
            if item and 'cidadeFavorita' in item:
                cidade = item['cidadeFavorita']

                # Lógica para obter o clima da cidade favorita (similar ao WeatherIntentHandler)
                api_address = "http://api.openweathermap.org/data/2.5/weather?appid=1171a0db15c1a723114891a7eaefc8ce&units=metric&q="
                url = api_address + cidade
                json_data = requests.get(url).json()
                formatted_json = traducoes_tempo.get(json_data['weather'][0]['main'], json_data['weather'][0]['main'])
                description = json_data['weather'][0]['description']
                temp = json_data['main']['temp']
                name = json_data['name']
                sys = json_data['sys']['country']
                description = json_data['weather'][0]['description']
                speak_output = f"O tempo em sua cidade favorita, {name}, é {formatted_json}, com temperatura de {temp}°C."
            else:
                speak_output = "Você ainda não definiu uma cidade favorita."
        except Exception as e:
            logger.error(f"Erro ao obter clima da cidade favorita: {e}")
            speak_output = "Desculpe, houve um erro ao obter o clima da sua cidade favorita."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )



class DefinirCidadeFavoritaIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("DefinirCidadeFavoritaIntent")(handler_input)

    def handle(self, handler_input):
        user_input = handler_input.request_envelope.request.intent.slots["city"].value

        try:
            table.put_item(
                Item={
                    'id': handler_input.request_envelope.session.user.user_id,
                    'cidadeFavorita': user_input
                }
            )

            speak_output = (
                f"Ok, defini {user_input} como sua cidade favorita. "
            )
        except Exception as e:
            speak_output = f"Ocorreu um erro ao definir a cidade favorita: {e}"

        return handler_input.response_builder.speak(speak_output).response



class WeatherIntentHandler(AbstractRequestHandler):
    """Handler for Weather Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("WeatherIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        city = slots['city'].value
        speak_output = ''
        api_address = "http://api.openweathermap.org/data/2.5/weather?appid=1171a0db15c1a723114891a7eaefc8ce&units=metric&q="
        url = api_address + city
        json_data = requests.get(url).json()
        formatted_json = traducoes_tempo.get(json_data['weather'][0]['main'], json_data['weather'][0]['main'])
        description = json_data['weather'][0]['description']
        temp = json_data['main']['temp']
        name = json_data['name']
        sys = json_data['sys']['country']
        description = json_data['weather'][0]['description']
        speak_output = "O tempo é {}, e a temperatura é {} °C, em {} no {}.".format(formatted_json, temp, name, sys)
        repromptOutput = " Voce quer a temperatura em outra cidade?"
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(repromptOutput)
                .response
        )




class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Ola, como posso te ajudar ?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye! see you soon."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "Voce acionou o " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(DefinirCidadeFavoritaIntentHandler())  
sb.add_request_handler(ClimaCidadeFavoritaIntentHandler())
sb.add_request_handler(WeatherIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()