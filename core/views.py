from django.core.mail import send_mail
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView

from core.models import Setting, Links
from core.forms import ControllerForm
import requests
from django_smarthouse_heroku.settings import SMART_HOME_API_URL, EMAIL_HOST, SMART_HOME_ACCESS_TOKEN


def get_data():
    try:
        url = SMART_HOME_API_URL#"https://smarthome.webpython.graders.eldf.ru/api/user.controller"
        headers = {f"Authorization": f"Bearer {SMART_HOME_ACCESS_TOKEN}"}
        response = requests.get(url, headers=headers)
        return response.json()['data']
    except:
        return "502"
class ControllerView(FormView):
    form_class = ControllerForm
    template_name = 'core/control.html'
    success_url = reverse_lazy('form')
    good_data = {}

    def get(self, request, *args, **kwargs):
        result = get_data()
        if result == '502':
            return HttpResponse(status=502)

        data = {}
        db_data = Setting.objects.all()
        for i in result:
            data[i['name']] = i['value']
        data["bedroom_target_temperature"] = db_data[0].value
        data["hot_water_target_temperature"] = db_data[1].value
        self.good_data = data
        return self.render_to_response(self.get_context_data(**kwargs),)
    def get_context_data(self, **kwargs):
        context = super(ControllerView, self).get_context_data()
        context['data'] = self.good_data
        l = Links.objects.get(pk=1)
        context['upwork_url'] = l.label
        return context

    # https://www.coursera.org/learn/python-for-web/discussions/weeks/7/threads/bdQ6pwZWEem_NQ6JYupVDA
    def get_initial(self):
        return {}


    def form_valid(self, form):
        db_data = Setting.objects.all()
        for i in db_data:
            print(i.label, i.value, i.controller_name)
        # форма валидна, но надо узнать значения на API
        try:
            r = requests.get(
                SMART_HOME_API_URL,
                headers={'Authorization': f'Bearer {SMART_HOME_ACCESS_TOKEN}'})
        except requests.RequestException:
            return HttpResponse('No connection to controllers API', status=502)
        if r.json()['status'] != 'ok':
            return HttpResponse('No connection to controllers API', status=502)

        api_data = r.json()
        good_dict = dict()
        for d in api_data['data']:
            good_dict[d['name']] = d['value']
        # print(good_dict, "\n")

        # сравниваем значения из валидной формы со значениями на API
        # если отличается то упаковыем значение из формы и отсылаем на API
        to_controllers = []
        if good_dict['bedroom_light'] != form.cleaned_data['bedroom_light']:
            to_controllers.append(
                {'name': 'bedroom_light', 'value': form.cleaned_data['bedroom_light']})
        if good_dict['bathroom_light'] != form.cleaned_data['bathroom_light']:
            to_controllers.append(
                {'name': 'bathroom_light', 'value': form.cleaned_data['bathroom_light']})
        if len(to_controllers) != 0:
            to_controllers = {'controllers': to_controllers}
            try:
                # print(to_controllers)
                r = requests.post(SMART_HOME_API_URL,headers={'Authorization': f'Bearer {SMART_HOME_ACCESS_TOKEN}'},
                    json=to_controllers)
            except requests.RequestException:
                return HttpResponse('No connection to controllers API', status=502)
            if r.json()['status'] != 'ok':
                return HttpResponse('No connection to controllers API', status=502)
        # запоминаем значения из валидной формы в базу
        db_data[0].value = form.cleaned_data['bedroom_target_temperature']
        db_data[1].value = form.cleaned_data['hot_water_target_temperature']
        db_data[0].save()
        db_data[1].save()
        return super(ControllerView, self).form_valid(form)

