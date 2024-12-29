from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        global num_machines
        global num_tasks

        # Récupération des données du formulaire
        num_machines = int(request.form['machines'])
        num_tasks = int(request.form['tasks'])

        # Validation du nombre de machines
        if num_machines < 2:
            return render_template('index.html', error="Le nombre de machines doit être au moins 2.")

        # Si les données sont valides, passer à l'étape suivante
        return render_template('input.html', num_machines=num_machines, num_tasks=num_tasks)

    return render_template('index.html')

@app.route('/input', methods=['POST'])
def input_page():
    processTimes = request.form.getlist('task_duration')
    processTimes = [int(i) for i in processTimes]
    k = 0
    pij = []
    for i in range(num_tasks):
        pij.append(processTimes[k:k + num_machines])
        k += num_machines

    # Les ei des tâches
    e = []
    for n in range(num_tasks):
        if pij[n][0] < pij[n][num_machines - 1]:
            e.append(1)
        else:
            e.append(-1)

    # Calcul de Pi1 + Pi2 etc.
    p = []
    for n in range(num_tasks):
        b = []
        for m in range(num_machines - 1):
            b.append(pij[n][m] + pij[n][m + 1])
        p.append(b)

    # Le min des sommes
    minList = [min(row) for row in p]

    # Calculer s
    s = [round(e[n] / minList[n], 4) if minList[n] != 0 else float('inf') for n in range(num_tasks)]

    # Ordre décroissant des s
    enumerated_list = list(enumerate(s))
    sorted_list = sorted(enumerated_list, key=lambda x: x[1], reverse=True)

    # Ordonnancer les tâches selon l'ordre décroissant des s
    sorted_indexes = [index for index, value in sorted_list]
    gupta = [x + 1 for x in sorted_indexes]

    # Calcul des temps de début et de fin pour le diagramme de Gantt
    start_times = [[0] * num_machines for _ in range(num_tasks)]
    end_times = [[0] * num_machines for _ in range(num_tasks)]

    for task_idx in range(num_tasks):
        task = sorted_indexes[task_idx]
        for machine_idx in range(num_machines):
            if machine_idx == 0:
                start_times[task][machine_idx] = end_times[sorted_indexes[task_idx - 1]][machine_idx] if task_idx > 0 else 0
            else:
                start_times[task][machine_idx] = max(
                    end_times[task][machine_idx - 1],
                    end_times[sorted_indexes[task_idx - 1]][machine_idx] if task_idx > 0 else 0
                )
            end_times[task][machine_idx] = start_times[task][machine_idx] + pij[task][machine_idx]

    c_max = max(end_times[sorted_indexes[-1]])  # Cmax

    return render_template('results.html',
                           processTimes=processTimes,
                           num_machines=num_machines,
                           num_tasks=num_tasks,
                           pij=pij,
                           e=e,
                           p=p,
                           minList=minList,
                           s=s,
                           gupta=gupta,
                           start_times=start_times,
                           end_times=end_times,
                           c_max=c_max)

if __name__ == '__main__':
    app.run(debug=True, port=5001)

