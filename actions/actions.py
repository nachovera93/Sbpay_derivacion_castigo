import datetime
from typing import Text, List, Any, Dict, Optional
from datetime import date, timedelta
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, Restarted, AllSlotsReset
import pymongo
global SiPaga
global NoPaga
global motivo
global tipo_contacto
global compromiso_p
global derivacion
global fecha_com
global entrega_info
SiPaga=None
NoPaga=None
motivo=None
tipo_contacto=0
compromiso_p=0
derivacion=None
fecha_com=None
entrega_info=None


CONNECTION_STRING = "mongodb://172.16.1.41:27017,172.16.1.42:27017,172.16.1.43:27017/?replicaSet=haddacloud-rs&readPreference=secondaryPreferred"
# CONNECTION_STRING = "mongodb://Admin:T3c4dmin1.@172.16.1.228:27017/data_warehouse?authSource=admin&readPreference=secondaryPreferred"
myclient = pymongo.MongoClient(CONNECTION_STRING)

organization_id=11

class SetNameAction(Action):
    def name(self):
        return "set_name_action"

    def run(self, dispatcher, tracker, domain):

        try:
            splits = tracker.sender_id
            customer_id,campaign_group,caller_id = splits.split('|')
            names = getNameByCustomerID(customer_id)
            print(names)
        except:
            names = "Jose Miguel"
        try: 
            deuda_mora, fecha_vcto = getDebtsByCustomerID(customer_id, campaign_group)
        except:
            deuda_mora = "10000"
            fecha_vcto = "01-01-1979"
        print(f"deuda_mora : {deuda_mora}")
        print(f"fecha_vcto : {fecha_vcto}")
        return [SlotSet("name", names),SlotSet("fecha_vcto", fecha_vcto), SlotSet("monto", deuda_mora)]



def getNameByCustomerID(customer_id):

    mydb = myclient["haddacloud-v2"]
    mycol = mydb["deudors"]

    x = mycol.find_one({ 'organization_id': int(organization_id), 'customer_id': str(customer_id)  })

    return x["nombre"]

def getDebtsByCustomerID(customer_id, campaign_group):

    mydb = myclient["haddacloud-v2"]
    mycol = mydb["debts"]

    x = mycol.find_one({  'organization_id': int(organization_id), 'customer_id': str(customer_id), 'group_campaign_id': int(campaign_group)  }, sort=[('updated_at', -1)])

    return x["deuda_total"], x["fecha_vcto"]


def month_converter(i):
       month = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
       return month[i-1]


        
    
class ActionSiPaga(Action):
    def name(self):
        return "action_si_paga"

    def run(self, dispatcher, tracker, domain):
        
        today_date = date.today()
        td = timedelta(3)
        fechaPago=str(today_date + td)
        print("Fecha de Pago: ",fechaPago)
        return [SlotSet("fecha_pago", fechaPago)]



class ActionRestart2(Action):
    """Resets the tracker to its initial state.
    Utters the restart template if available."""

    def name(self) -> Text:
        return "action_restart2"

    async def run(self, dispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [Restarted()]

class ActionSlotReset(Action):
    def name(self):
        return 'action_slot_reset'
    def run(self, dispatcher, tracker, domain):
        return[AllSlotsReset()]


class ActionGuardarConoce(Action):

    def name(self) -> Text:
        return "action_guardar_conoce_o_no"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        conoce_o_no = tracker.get_slot("conoce_o_no")
        if tracker.get_slot("conoce_o_no") is None:
            print("Es None ..")
        print("conoce_o_no: ", conoce_o_no)
            #dispatcher.utter_message(text=f"Razón: {Razón}")
        return []


class ActionRecibirEsoNo(Action):

    def name(self) -> Text:
        return "action_recibir_es_o_no"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        es_o_no = tracker.get_slot("es_o_no")
        print("es_o_no: ", es_o_no)
            #dispatcher.utter_message(text=f"Razón: {Razón}")
        return []


conoce_intent=None
class ActionConoceONo(Action):
    def name(self):
        return "action_save_conoce_o_no"

    def run(self, dispatcher, tracker, domain):
        global conoce_intent
        # Obtener la intención actual
        latest_message = tracker.latest_message
        conoce_intent = latest_message['intent']['name']
        print(f'conoce o no: {conoce_intent}')


paga_intent=None
class ActionPagaONo(Action):
    def name(self):
        return "action_save_intent_paga_o_no"

    def run(self, dispatcher, tracker, domain):
        global paga_intent
        # Obtener la intención actual
        latest_message = tracker.latest_message
        paga_intent = latest_message['intent']['name']
        print(f'paga_intent : {paga_intent}')

es_o_no_intent=None


class ActionConoceONo(Action):
    def name(self):
        return "action_es_o_no"

    def run(self, dispatcher, tracker, domain):
        global es_o_no_intent
        # Obtener la intención actual
        latest_message = tracker.latest_message
        es_o_no_intent = latest_message['intent']['name']
        print(f'es_o_no_intent: {es_o_no_intent}')


class ActionSiPaga(Action):
    def name(self):
        return "action_save_data"

    def run(self, dispatcher, tracker, domain):
        mydb = myclient["haddacloud-v2"]
        mycol = mydb["voicebot-interactions"]


        splits = tracker.sender_id
        customer_id,campaign_group,caller_id = splits.split('|')
        print("-------------------------------------------------------------")
        print(tracker.slots)

        # Obtener la intención actual
        latest_message = tracker.latest_message
        current_intent = latest_message['intent']['name']
        
        # Imprimir el nombre de la intención
        print(f'current_intent: {current_intent}')
        print(f'current_intent: {type(current_intent)}')
        if(current_intent=="opcion_1"):
            current_intent="Renegociar"
        if(current_intent=="opcion_2"):
            current_intent="Reagendar"
        if(current_intent=="opcion_3"):
            current_intent="Asesoria"
        name=tracker.slots["name"]
        es_persona_correcta=tracker.slots["es_persona_correcta"]
        conoce_o_no=tracker.slots["conoce_o_no"]
        fecha_vcto=tracker.slots["fecha_vcto"]
        fecha_pago=tracker.slots["fecha_pago"]
        monto=tracker.slots["monto"]
        paga_o_no=tracker.slots["paga_o_no"]
        fecha_vcto=tracker.slots["fecha_vcto"]
        opcion_pago=tracker.slots["opcion_pago"]

        print(f'name: {name}')
        print(f'es_persona_correcta {es_o_no_intent}')
        print(f'conoce_o_no: {conoce_intent}')
        print(f'fecha_vcto: {fecha_vcto}')
        print(f'monto: {monto}')
        print(f'paga_o_no: {paga_intent}')
        print(f'opcion_pago: {current_intent}')
        print(f'conoce_intent: {conoce_intent}')
        


        print("-------------------------------------------------------------")

        bulk_updates=[]
        update = pymongo.UpdateOne(
            {
                "customer_id": str(customer_id),
                "organization_id": int(organization_id),
                "group_campaign_id": int(campaign_group),
                "caller_id": str(caller_id)
            },
            {
                "$set": {
                    "es_persona_correcta": es_o_no_intent,
                    "conoce_o_no": conoce_intent,
                    "opcion_pago": current_intent,
                    "paga_o_no": paga_intent,
                    "name": name,
                    "monto": monto,
                    "fecha_vcto": fecha_vcto,
                    "fecha_pago": fecha_pago,
                    "created_at": datetime.datetime.now(),
                    "updated_at": datetime.datetime.now()
                }},
                upsert=True
            )
        bulk_updates.append(update)
        result = mycol.bulk_write(bulk_updates)
        #print(f'{result.modified_count} Updateds')
        
        name=None
        es_persona_correcta=None
        conoce_o_no=None
        fecha_vcto=None
        fecha_pago=None
        monto=None
        paga_o_no=None
        fecha_vcto=None
        opcion_pago=None

        return []
    





class ActionRepeatLastQuestion(Action):

    def name(self) -> Text:
        return "action_repeat_last_question"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        last_bot_utterance = None

        for event in reversed(tracker.events):
            if event.get("event") == "bot":
                last_bot_utterance = event.get("text")
                break

        if last_bot_utterance:
            dispatcher.utter_message(text=last_bot_utterance)
        else:
            dispatcher.utter_message(text="Lo siento, no tengo información sobre la última pregunta.")

        return []

class ActionFallback(Action):

    def name(self) -> Text:
        return "action_default_fallback"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # Obtener la intención predicha
        predicted_intent = tracker.latest_message['intent']['name']

        # Establecer la ranura 'predicted_intent' con la intención predicha
        return [SlotSet("predicted_intent", predicted_intent)]