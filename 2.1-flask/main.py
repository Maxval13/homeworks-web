from typing import Type
from flask import Flask, jsonify, request
from flask.views import MethodView
from model import Ads, Session
import pydantic
from sqlalchemy.exc import IntegrityError
from shema import CreateAds

app = Flask('app')


class HttpError(Exception):

    def __init__(self, status_code: int, message: str | dict | list):
        self.status_code = status_code
        self.message = message


@app.errorhandler(HttpError)
def error_handler(er: HttpError):
    response = jsonify({'status': 'error', 'message': er.message})
    response.status_code = er.status_code
    return response


def validate(validation_schema: Type[CreateAds], json_data):
    try:
        pydantic_obj = validation_schema(**json_data)
        return pydantic_obj.dict(exclude_none=True)
    except pydantic.ValidationError as er:
        raise HttpError(400, er.errors())


def get_ads(session: Session, ads_id: int):
    ads = session.get(Ads, ads_id)
    if ads is None:
        raise HttpError(404, "ads not found")
    return ads


class AdsView(MethodView):

    def get(self, ads_id: int):  # получать объявление
        with Session() as session:
            ads = get_ads(session, ads_id)
            return jsonify({
                'id': ads.id,
                'heading': ads.heading,
                'description': ads.description,
                'creation_time': ads.creation_time.isoformat(),
                'owner': ads.owner
            })

    def post(self):  # создавать объявление
        validate_data = validate(CreateAds, request.json)
        with Session() as session:
            new_ads = Ads(**validate_data)
            session.add(new_ads)
            try:
                session.commit()
            except IntegrityError as er:
                raise HttpError(409, "ads already exist")
            return jsonify({'id': new_ads.id})

    def delete(self, ads_id):  # удалять объявление
        with Session() as session:
            ads = get_ads(session, ads_id)
            session.delete(ads)
            session.commit()
            return jsonify({'status': f'deleted {ads_id}'})


ads_view = AdsView.as_view('adss')

app.add_url_rule('/ads/<int:ads_id>', view_func=ads_view, methods=['GET', 'DELETE'])
app.add_url_rule('/ads', view_func=ads_view, methods=['POST'])

if __name__ == '__main__':
    app.run()
