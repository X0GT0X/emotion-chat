from flask import Response, request
from flask_restful import Resource
from database.models import Subscriber
from pywebpush import webpush
import datetime
import json

class Subscription(Resource):

    def post(self):
        try:
            subscription_info = request.get_json()
            subscriber = Subscriber.objects(subscriptionInfo=subscription_info).first()
            if not subscriber:
                subscriber = Subscriber()
                subscriber.created = datetime.datetime.utcnow()
                subscriber.subscriptionInfo = subscription_info
            subscriber.modified = datetime.datetime.utcnow()
            subscriber.save()
            return Response(json.dumps({id: subscriber.id}), mimetype="application/json", status=201)
        except Exception as e:
            return {"message": "Something went wrong."}, 400


class Notifications(Resource):

    WEBPUSH_VAPID_PRIVATE_KEY = 'xxx'

    def post(self, id):

        body = request.get_json()

        try:
            subscriber = Subscriber.objects(id=id).first()
            webpush(
                subscription_info=subscriber.subscriptionInfo,
                data=body.get("data"),
                vapid_private_key=self.WEBPUSH_VAPID_PRIVATE_KEY
            )
        except Exception as e:
            return {"message": "Something went wrong."}, 400

        return {"message": "Notification was sent"}, 201
