import streamlit as st
import pandas as pd
import joblib
import datetime
import locale

st.set_page_config(layout='centered', initial_sidebar_state='auto')

st.title('Выбор лучшего времени и места для пикника на Финском заливе')

st.subheader('Сроки')
st.slider('Выберите число большее / равное длительности', 1, 31, key='time')
time_input = st.session_state.time

st.subheader('Длительность')
st.slider('Выберите число меньшее / равное срокам', 1, 5, key='duration')
duration_input = st.session_state.duration

if time_input < duration_input:
    error1 = True
    st.error('**Сроки** и **длительность** не соответствуют требованиям под заголовками.')
else:
    error1 = None

st.subheader('Осадка яхты')
st.text_input('Введите число > 0', autocomplete='', placeholder='', key='sediment')
sediment_input = st.session_state.sediment

st.subheader('Место стоянки')
st.selectbox('', ['', 'на воде', 'у пристани', 'в порту', 'у берега'], key='stop')
stop_input = st.session_state.stop

if (stop_input == 'на воде') or (stop_input == 'у берега'):
    error2 = None
    if sediment_input == '':
        error2 = True
        st.error('Введите **осадку** или измените **место стоянки** на "у пристани" / "в порту" / пустое.')
    elif (type(sediment_input) != int) and (type(sediment_input) != float):
        try:
            sediment_input = float(sediment_input.replace(',', '.'))
            if sediment_input <= 0:
                error2 = True
                st.error('**Осадка** не должна быть меньше / равна 0.')
        except:
            error2 = True
            st.error('Формат **осадки** должен быть **числовым**. (1 | 1,2 | 1.2)')
else:
    error2 = None

headers_list = ['Пейзаж', 'Береговая инфраструктура', 'Высота берега', 'Температура воздуха', 'Осадки, облачность',
                'Оптимальный ветер', 'Оптимальные волны']
labels_list = [''] * 3 + ['по °C'] + [''] + ['в баллах'] * 2
selections_list = [['', 'сосновый лес', 'смешаный леc', 'песчаный берег', 'каменный берег'],
                   ['', 'дикое место', 'дорога', 'оборудованное место', 'места для ночлега', 'рестораны'],
                   ['', 'высокий', 'средний', 'низкий'],
                   ['', '0-7°', '8-15°', '16-23°', '24-31°', '32-39°'],
                   ['', 'ясно', 'слегка облачно', 'облачно', 'пасмурно', 'сильная облачность', 'лёгкий дождь', 'дождь',
                    'дождь и снег', 'небольшой снегопад', 'снегопад'],
                   ['', '0-3', '0-5', '0-7', '0-9', '0-12'],
                   ['', '0-2', '0-4', '0-6', '0-8', '0-9']]
keys_list = ['landscape', 'infrastructure', 'altitude_coast', 'temperature', 'clouds', 'wind', 'waves']

for header, label, selection, key in zip(headers_list, labels_list, selections_list, keys_list):
    st.subheader(header)
    st.selectbox(label, selection, key=key)

landscape_input = st.session_state.landscape
infrastructure_input = st.session_state.infrastructure
altitude_coast_input = st.session_state.altitude_coast
temperature_input = st.session_state.temperature
clouds_input = st.session_state.clouds
wind_input = st.session_state.wind
waves_input = st.session_state.waves

if (stop_input == '') and (landscape_input == '') and \
        (infrastructure_input == '') and (altitude_coast_input == '') and \
        (temperature_input == '') and (clouds_input == '') and \
        (wind_input == '') and (waves_input == ''):
    error3 = True
    st.error('**Все поля выбора пустые.**')
else:
    error3 = None

if (error1 is None) and (error2 is None) and (error3 is None):
    done_button = st.button('Готово')
    if done_button:
        non_dynamic_data = pd.read_excel('non_dynamic.xlsx')
        temperature_data = pd.read_excel('dynamic.xlsx', sheet_name='temperature')
        wind_data = pd.read_excel('dynamic.xlsx', sheet_name='wind')
        waves_data = pd.read_excel('dynamic.xlsx', sheet_name='waves')
        clouds_data = pd.read_excel('dynamic.xlsx', sheet_name='clouds')
        places = pd.read_excel('places.xlsx')

        dynamic_datas_list = [temperature_data, wind_data, waves_data, clouds_data]
        compared_columns_list = ['temperature_wind', 'temperature_waves', 'temperature_cloud', 'wind_waves',
                                 'wind_cloud', 'waves_cloud']

        final_results = pd.DataFrame()

        if (stop_input != '') or (landscape_input != '') or \
                (infrastructure_input != '') or (altitude_coast_input != ''):
            inputs_list = [stop_input, landscape_input, infrastructure_input, altitude_coast_input]
            non_dynamic_columns_list = ['stop', 'landscape', 'infrastructure', 'altitude_coast']

            for input, column in zip(inputs_list, non_dynamic_columns_list):
                for index in range(non_dynamic_data.shape[0]):
                    if input != '':
                        if input in str(non_dynamic_data.loc[index, column]):
                            non_dynamic_data.loc[index, column] = 1
                        else:
                            non_dynamic_data.loc[index, column] = 0
                    else:
                        non_dynamic_data.loc[index, column] = 1

            for index in range(non_dynamic_data.shape[0]):
                if stop_input == 'на воде':
                    non_dynamic_data['stop'] = 1
                    if sediment_input < non_dynamic_data.loc[index, 'distance_150m']:
                        non_dynamic_data.loc[index, 'stop_distance'] = 150
                    elif sediment_input < non_dynamic_data.loc[index, 'distance_300m']:
                        non_dynamic_data.loc[index, 'stop_distance'] = 300
                    else:
                        non_dynamic_data.loc[index, 'stop_distance'] = 450
                elif stop_input == 'у берега':
                    if sediment_input < non_dynamic_data.loc[index, 'depth_coast']:
                        non_dynamic_data.loc[index, 'stop'] = 1
                    else:
                        non_dynamic_data.loc[index, 'stop'] = 0

            non_dynamic_result = non_dynamic_data.isin([1]).sum(axis=1)
        else:
            non_dynamic_result = [4] * non_dynamic_data.shape[0]

        if (temperature_input != '') or (clouds_input != '') or \
                (wind_input != '') or (waves_input != ''):
            dynamic_data_classifier = joblib.load(open('dynamic_data_classifier.pkl', 'rb'))

            inputs_list = [temperature_input, wind_input, waves_input, clouds_input]
            dynamic_columns_list = ['temperature', 'wind', 'waves', 'clouds']

            dynamic_results = pd.DataFrame()

            for data, input in zip(dynamic_datas_list, inputs_list):
                data.iloc[:, time_input + 1:] = 0
                for column in data.columns:
                    if input != '':
                        data.loc[(data[column] == input), column] = 1
                        data.loc[(data[column] != 1), column] = 0
                        data['picnic_duration'] = duration_input

            for input, data, column in zip(inputs_list, dynamic_datas_list, dynamic_columns_list):
                if input != '':
                    dynamic_results[column] = dynamic_data_classifier.predict(data)
                else:
                    dynamic_results[column] = 'x'

            if (temperature_input == '') or (clouds_input == '') or \
                    (wind_input == '') or (waves_input == ''):
                for column in dynamic_columns_list:
                    if dynamic_results.loc[0, column] == 'x':
                        dynamic_results[column] = dynamic_results[dynamic_results != 'x'].iloc[:, 0]

            for column in compared_columns_list:
                final_results[column] = [0] * dynamic_results.shape[0]

            for column1, column2 in zip(['temperature'] * 3 + ['wind'] * 2 + ['waves'],
                                        ['wind'] + ['waves'] + ['clouds'] + ['waves'] + ['clouds'] * 2):
                for compared_column in compared_columns_list:
                    for index in range(dynamic_results.shape[0]):
                        if (column1 in compared_column) and (column2 in compared_column):
                            if dynamic_results.loc[index, column1] == dynamic_results.loc[index, column2]:
                                final_results.loc[index, compared_column] = 1
        else:
            for column in compared_columns_list:
                final_results[column] = [1] * non_dynamic_data.shape[0]

        final_results.insert(0, 'non_dynamic_result', non_dynamic_result)

        final_results_regressor = joblib.load(open('final_results_regressor.pkl', 'rb'))
        final_result = pd.DataFrame(final_results_regressor.predict(final_results))
        max_final_result = final_result.idxmax(axis=0, skipna=True)

        locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
        today = datetime.date.today()

        if final_result.max()[0] > 9.5:
            if (temperature_input != '') or (clouds_input != '') or \
                    (wind_input != '') or (waves_input != ''):
                dynamic_columns_list_sorted = dynamic_columns_list.sort(reverse=True)
                for column in dynamic_columns_list_sorted:
                    for compared_column in compared_columns_list:
                        if (column in compared_column) and (
                                final_results.loc[max_final_result[0], compared_column] == 1):
                            day = int(dynamic_results.loc[max_final_result[0], column])
                            break

                day1 = (today + datetime.timedelta(day - 1)).strftime('%d %B')
                day2 = (today + datetime.timedelta(day - 1 + duration_input)).strftime('%d %B')
                days = f'{day1}-{day2}'
            else:
                days = ''

            place = places.loc[max_final_result[0]][0]

            if stop_input == 'на воде':
                meters = non_dynamic_data.loc[max_final_result[0], 'stop_distance']
                print(f'Место найдено! Лучшим вариантом для вас будет {place} {days}. '
                      f'Остановиться желательно дальше {meters} метров от берега.')
            else:
                print(f'Место найдено! Лучшим вариантом для вас будет {place} {days}.')
        else:
            def prepare_dynamic_data(data):
                del data['picnic_duration']
                data.columns = days_list
                data = pd.concat([places, data], axis=1)
                data.insert(0, 'Процент релевантности места', final_result * 10)
                data = data.sort_values('Процент релевантности места', ascending=False). \
                    drop_duplicates(subset='Места', keep='first').reset_index(drop=True)
                return data


            st.warning('К сожалению, на данный момент идеально подходящего вам места не нашлось:( Вы можете изменить '
                       'параметры поиска или посмотреть менее подходящие места')

            days = [today + datetime.timedelta(days=number) for number in range(31)]
            days_list = []
            for day in days:
                days_list.append(day.strftime('%d %B'))

            non_dynamic_output = pd.read_excel('non_dynamic_output.xlsx')
            non_dynamic_output = pd.concat([places, non_dynamic_output], axis=1)
            non_dynamic_output.insert(0, 'Процент релевантности места', final_result * 10)
            non_dynamic_output = non_dynamic_output.sort_values('Процент релевантности места', ascending=False). \
                drop_duplicates(subset='Места', keep='first').reset_index(drop=True)

            temperature_data = prepare_dynamic_data(temperature_data)
            wind_data = prepare_dynamic_data(wind_data)
            waves_data = prepare_dynamic_data(waves_data)
            clouds_data = prepare_dynamic_data(clouds_data)

            st.subheader('Менее подходящие места')
            st.radio('', ('Нединамические параметры', 'Температура воздуха', 'Осадки, облачность', 'Ветер', 'Волны')
                     , key='params_output')
            params_output_radio = st.session_state.params_output
            st.write('Места отсортированы в порядке убывания подходящих параметров.')

            if params_output_radio == 'Температура воздуха':
                st.dataframe(temperature_data)
            elif params_output_radio == 'Осадки, облачность':
                st.dataframe(clouds_data)
            elif params_output_radio == 'Ветер':
                st.dataframe(wind_data)
            elif params_output_radio == 'Волны':
                st.dataframe(waves_data)
            else:
                st.dataframe(non_dynamic_output)

