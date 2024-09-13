import os
import json
import requests
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from itertools import cycle
import time
import threading
import random
import sys
import psutil
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from colorama import Fore, Style, init
import subprocess

init(autoreset=True)
#comment1
#comment2
monitoring = False

spinner = cycle(['/', '-', '\\', '|'])

def select_file():
    Tk().withdraw()
    filename = askopenfilename(filetypes=[("Text files", "*.txt")])
    return filename

def save_path_to_json(file_path, json_path="file_path.json"):
    data = {"file_path": file_path}
    with open(json_path, 'w') as json_file:
        json.dump(data, json_file)

def load_path_from_json(json_path="file_path.json"):
    if os.path.exists(json_path):
        with open(json_path, 'r') as json_file:
            data = json.load(json_file)
        return data["file_path"]
    return None

def load_database(filename):
    phrases = []
    responses = []
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            if ';' in line:
                phrase, response = line.strip().split(';', 1)
                phrases.append(phrase)
                responses.append(response)
    return phrases, responses

def get_internet_search_results(query):
    try:
        response = requests.get(
            'https://www.googleapis.com/customsearch/v1',
            params={'key': 'AIzaSyDgh0NGTEqtDnzbizIMHHCYDaswVMjgmzo', 'cx': 'c192e8b9aa45642b6', 'q': query}
        )
        response.raise_for_status()
        results = response.json()
        if 'items' in results:
            return results['items'][0]['snippet'], results['items'][0]['link']
        return 'Результати пошуку не знайдені.', ''
    except requests.RequestException as e:
        return f'Помилка при запиті сторінки: {e}', ''

def preprocess_input(user_input):
    normalized_input = user_input.lower().strip()
    if normalized_input and normalized_input[-1] not in ['.', '?', '!']:
        normalized_input += '?'
    return normalized_input

def get_memory_analysis():
    def format_size(size_in_bytes):
        size_in_mb = size_in_bytes / (2**20)
        size_in_gb = size_in_bytes / (2**30)
        
        if size_in_mb < 1024:
            return f"{size_in_mb:.2f} МБ"
        else:
            return f"{size_in_gb:.2f} ГБ"
    
    memory = psutil.virtual_memory()
    disks = psutil.disk_partitions()
    disk_info = []
    
    for disk in disks:
        usage = psutil.disk_usage(disk.mountpoint)
        disk_info.append(f"Диск: {disk.device}, Шлях монтування: {disk.mountpoint}, "
                         f"Всього: {format_size(usage.total)}, Використано: {format_size(usage.used)}, "
                         f"Вільно: {format_size(usage.free)}")
    
    memory_info = (f"Оперативна пам'ять: Всього: {format_size(memory.total)}, "
                   f"Використано: {format_size(memory.used)}, Вільно: {format_size(memory.available)}")
    
    return memory_info, disk_info
# Second comment
def clean_temp_files():
    try:
        command = "del /q /f /s %TEMP%\* > NUL 2>&1"
        result = os.system(command)
        if result == 0:
            return True, None
        else:
            return False, f"Команда завершилася з помилкою: {result}"
    except Exception as e:
        return False, str(e)

def spinner_animation(stop_event, spinner):
    sys.stdout.write("\033[?25l")
    while not stop_event.is_set():
        sys.stdout.write(Fore.MAGENTA + next(spinner))
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write('\b')
    sys.stdout.write("\033[?25h")
  # analiting of energy  
def get_energy_analysis():
    battery = psutil.sensors_battery()
    percent = battery.percent
    power_plugged = battery.power_plugged
    
    if power_plugged:
        remaining_time = '∞'
        if percent < 100:
            time_to_full_charge = (100 - percent) * 2
            hours = time_to_full_charge // 60
            minutes = time_to_full_charge % 60
            if hours > 0:
                time_to_full_charge_str = f"{hours} годин {minutes} хвилин"
            else:
                time_to_full_charge_str = f"{minutes} хвилин"
        else:
            time_to_full_charge_str = "повністю заряджено"
    else:
        remaining_minutes = percent * 3
        hours = remaining_minutes // 60
        minutes = remaining_minutes % 60
        remaining_time = f"{hours} годин {minutes} хвилин"
        time_to_full_charge_str = "зарядка не йде"
    
    battery_info = (
        f"Відсоток заряду: {percent}%\n"
        f"Тип живлення: {'мережеве' if power_plugged else 'акумуляторне'}\n"
        f"Залишившийся час роботи: {remaining_time}\n"
        f"До повної зарядки: {time_to_full_charge_str}"
    )
    
    return battery_info

def get_system_analysis():
    def get_battery_status():
        try:
            battery = psutil.sensors_battery()
            if battery:
                percent = battery.percent
                return f"Батарея: {'В нормі' if percent > 20 else 'Розряджена'} ({percent}%)"
            return "Батарея: не вдалося отримати дані"
        except Exception as e:
            return f"Батарея: помилка отримання даних ({e})"

    def get_memory_status():
        try:
            mem = psutil.virtual_memory()
            ram_used = mem.used / (1024 ** 3)
            ram_total = mem.total / (1024 ** 3)
            ram_percentage = mem.percent
            return f"Оперативна пам'ять: {ram_used:.2f} ГБ з {ram_total:.2f} ГБ (використано {ram_percentage}%)"
        except Exception as e:
            return f"Оперативна пам'ять: помилка отримання даних ({e})"

    def get_disk_status():
        try:
            disk = psutil.disk_usage('/')
            disk_used = disk.used / (1024 ** 3)
            disk_total = disk.total / (1024 ** 3)
            disk_percentage = disk.percent
            return f"Внутрішня пам'ять: {disk_used:.2f} ГБ з {disk_total:.2f} ГБ (використано {disk_percentage}%)"
        except Exception as e:
            return f"Внутрішня пам'ять: помилка отримання даних ({e})"

    def get_virtual_memory_status():
        try:
            swap = psutil.swap_memory()
            swap_used = swap.used / (1024 ** 3)
            swap_total = swap.total / (1024 ** 3)
            swap_percentage = swap.percent
            return f"Віртуальна пам'ять: {swap_used:.2f} ГБ з {swap_total:.2f} ГБ (використано {swap_percentage}%)"
        except Exception as e:
            return f"Віртуальна пам'ять: помилка отримання даних ({e})"

    def get_network_status():
        try:
            if psutil.net_if_addrs():
                result = subprocess.run(
                    ["powershell", "-Command", "Test-Connection -ComputerName google.com -Count 1"],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    return "Мережа: підключено до Інтернету"
                return "Мережа: помилка підключення до Інтернету"
            return "Мережа: немає мережевих інтерфейсів"
        except Exception as e:
            return f"Мережа: помилка отримання даних ({e})"

    def get_system_uptime():
        try:
            uptime_seconds = time.time() - psutil.boot_time()
            uptime_hours = uptime_seconds / 3600
            return f"Час роботи системи: {uptime_hours:.2f} годин"
        except Exception as e:
            return f"Час роботи системи: помилка отримання даних ({e})"

    def get_cpu_usage():
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            return f"Завантаженість CPU: {cpu_usage}%"
        except Exception as e:
            return f"Завантаженість CPU: помилка отримання даних ({e})"

    def get_number_of_cores():
        try:
            cores = psutil.cpu_count(logical=False)
            logical_cores = psutil.cpu_count(logical=True)
            return f"Кількість ядер CPU: {cores} фізичних, {logical_cores} логічних"
        except Exception as e:
            return f"Кількість ядер CPU: помилка отримання даних ({e})"

    def get_boot_time():
        try:
            boot_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(psutil.boot_time()))
            return f"Час останнього перезавантаження: {boot_time}"
        except Exception as e:
            return f"Час останнього перезавантаження: помилка отримання даних ({e})"

    def get_open_ports():
        try:
            connections = psutil.net_connections()
            open_ports = [conn.laddr.port for conn in connections if conn.status == 'LISTEN']
            if open_ports:
                return f"Відкриті порти: {', '.join(map(str, open_ports))}"
            return "Відкриті порти: немає"
        except Exception as e:
            return f"Відкриті порти: помилка отримання даних ({e})"

    def get_logged_users():
        try:
            users = psutil.users()
            if users:
                user_info = "\n".join([f"{user.name} (увійшов до системи: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(user.started))})" for user in users])
                return f"Користувачі, що увійшли до системи:\n{user_info}"
            return "Користувачі, що увійшли до системи: дані відсутні"
        except Exception as e:
            return f"Користувачі, що увійшли до системи: помилка отримання даних ({e})"

    def get_running_processes():
        try:
            processes = [(p.info["name"], p.info["cpu_percent"]) for p in psutil.process_iter(attrs=["name", "cpu_percent"])]
            sorted_processes = sorted(processes, key=lambda x: x[1], reverse=True)
            top_processes = sorted_processes[:5]
            processes_info = "\n".join([f"{name}: {cpu}%" for name, cpu in top_processes])
            return f"Топ-5 процесів з використання CPU:\n{processes_info}"
        except Exception as e:
            return f"Процеси: помилка отримання даних ({e})"

    battery_status = get_battery_status()
    memory_status = get_memory_status()
    disk_status = get_disk_status()
    virtual_memory_status = get_virtual_memory_status()
    network_status = get_network_status()
    system_uptime = get_system_uptime()
    cpu_usage = get_cpu_usage()
    number_of_cores = get_number_of_cores()
    boot_time = get_boot_time()
    open_ports = get_open_ports()
    logged_users = get_logged_users()
    running_processes = get_running_processes()

    system_info = (
        f"{battery_status}\n"
        f"{memory_status}\n"
        f"{disk_status}\n"
        f"{virtual_memory_status}\n"
        f"{network_status}\n"
        f"{system_uptime}\n"
        f"{cpu_usage}\n"
        f"{number_of_cores}\n"
        f"{boot_time}\n"
        f"{open_ports}\n"
        f"{logged_users}\n"
        f"{running_processes}"
    )

    return system_info
    
def optimize_energy_usage():
    def terminate_high_resource_processes(threshold=80):
        terminated = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                if proc.info['name'] in ['System Idle Process', 'System']:
                    continue

                if proc.info['cpu_percent'] > threshold:
                    proc.kill()
                    terminated.append(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                continue
        return terminated

    def set_power_saving_mode():
        try:
            os.system("powercfg /setactive SCHEME_MIN")
            return True
        except Exception as e:
            return False, str(e)

    terminated_processes = terminate_high_resource_processes()
    power_mode_set = set_power_saving_mode()

    if terminated_processes:
        processes_message = "Завершені процеси: " + ", ".join(terminated_processes)
    else:
        processes_message = "Немає процесів для завершення"

    if power_mode_set:
        power_mode_message = "Режим енергозбереження активовано"
    else:
        power_mode_message = "Не вдалося активувати режим енергозбереження"

    energy_optimization_info = (
        f"{processes_message}\n"
        f"{power_mode_message}"
    )

    return energy_optimization_info

def monitor_battery():
    last_status = None
    optimization_triggered = False

    while monitoring:
        try:
            battery = psutil.sensors_battery()
            if battery:
                percent = battery.percent
                status = ""

                if percent == 100:
                    status = "заряджена повністю"
                elif 70 <= percent <= 99:
                    status = "високий рівень заряда"
                elif 35 <= percent <= 69:
                    status = "середній рівень заряда"
                elif 16 <= percent <= 34:
                    status = "низький рівень заряда"
                elif 0 <= percent <= 15:
                    status = "критичний рівень заряда"
                else:
                    status = "невідомий рівень заряда"

                if last_status in ["низький рівень заряда", "критичний рівень заряда"] and status not in ["низький рівень заряда", "критичний рівень заряда"]:
                    optimization_triggered = False

                if status != last_status:
                    if status == "низький рівень заряда" and not optimization_triggered:
                        time.sleep(0.2)
                        type_text(f"---\nОповіщення системи контролю:\nБатарея: {status}", Fore.YELLOW)
                        type_text("Повідомлення: оптимізуйте споживання енергії", Fore.YELLOW)
                        sys.stdout.write(Fore.WHITE + "Ваш вопрос: ")
                        sys.stdout.flush()
                        optimization_triggered = True

                    elif status == "критичний рівень заряда" and (not optimization_triggered or last_status == "низький рівень заряда"):
                        time.sleep(0.2)
                        type_text(f"---\nОповіщення системи контролю:\nБатарея: {status}", Fore.YELLOW)
                        type_text("Повідомлення:\nЗапущено оптимізацію споживання енергії", Fore.YELLOW)
                        sys.stdout.write(Fore.MAGENTA + "Оптимізую ")
                        sys.stdout.flush()

                        stop_spinner = threading.Event()

                        def perform_energy_optimization():
                            global energy_optimization_info
                            energy_optimization_info = optimize_energy_usage()
                            stop_spinner.set()

                        spinner_thread = threading.Thread(target=spinner_animation, args=(stop_spinner, spinner))
                        optimization_thread = threading.Thread(target=perform_energy_optimization)

                        spinner_thread.start()
                        optimization_thread.start()

                        optimization_thread.join()
                        spinner_thread.join()

                        sys.stdout.write('\r' + ' ' * len("Оптимізую |") + '\r')
                        sys.stdout.flush()

                        type_text("Споживання енергії оптимізовано, режим енергозбереження активовано", Fore.YELLOW)
                        sys.stdout.write(Fore.WHITE + "Запит: ")
                        sys.stdout.flush()

                        optimization_triggered = True

                    last_status = status

            else:
                type_text("Помилка отримання даних про батарею\n", Fore.RED)

        except Exception as e:
            type_text(f"Помилка: {e}\n", Fore.RED)

        time.sleep(10)

def type_text(text, color=Fore.LIGHTGREEN_EX, delay=0.05):
    for char in text:
        sys.stdout.write(color + char)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write('\n')
    
def main():
    global memory_info, disk_info, monitoring

    json_path = "file_path.json"

    if not os.path.exists(json_path):
        file_path = select_file()
        if file_path:
            save_path_to_json(file_path, json_path)
        else:
            print("Файл не був обран. Вихід.")
            return

    file_path = load_path_from_json(json_path)
    if not file_path:
        print("Не вдалось завантажити шлях до файла. Вихід.")
        return

    phrases, responses = load_database(file_path)

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(phrases)
    nbrs = NearestNeighbors(n_neighbors=1, algorithm='auto').fit(X)

    spinner = cycle(['/', '-', '\\', '|'])

    while True:
        user_input = input(Fore.WHITE + "Запит: ").strip()
        if user_input.lower() == 'exit':
            break

        if user_input.lower().startswith("пошук:"):
            query = user_input[7:].strip()
            sys.stdout.write(Fore.MAGENTA + "Пошук ")
            sys.stdout.flush()

            stop_spinner = threading.Event()
            snippet = ''
            link = ''

            def perform_search():
                nonlocal snippet, link
                snippet, link = get_internet_search_results(query)
                stop_spinner.set()

            spinner_thread = threading.Thread(target=spinner_animation, args=(stop_spinner, spinner))
            search_thread = threading.Thread(target=perform_search)

            spinner_thread.start()
            search_thread.start()

            search_thread.join()
            spinner_thread.join()

            sys.stdout.write('\r' + ' ' * len("Пошук |") + '\r')
            sys.stdout.flush()

            if snippet:
                type_text(f'Знайдений результат: {snippet}')
                type_text(f'Посилання: {link}')
            else:
                type_text("Результати пошуку не знайдені.")
        
        elif user_input.lower() == "контроль: вкл":
            if not monitoring:
                sys.stdout.write(Fore.MAGENTA + "Під'єднуюсь ")
                sys.stdout.flush()

                stop_spinner = threading.Event()

                def connect_battery_monitor():
                    global monitoring, battery_info
                    monitoring = True
                    battery_info = ""
                    
                    battery = psutil.sensors_battery()
                    time.sleep(random.uniform(1, 2))
                    stop_spinner.set()

                    sys.stdout.write('\r' + ' ' * len("Під'єднуюсь |") + '\r')
                    sys.stdout.flush()

                    if battery:
                        percent = battery.percent
                        if percent == 100:
                            status = "заряджений повністю"
                        elif 70 <= percent <= 99:
                            status = "високий"
                        elif 35 <= percent <= 69:
                            status = "середній"
                        elif 16 <= percent <= 34:
                            status = "низький"
                        elif 0 <= percent <= 15:
                            status = "критичний"
                        else:
                            status = "невідомий"

                        battery_info = f"Живлення під контролем\nПоточний рівень заряду: {percent}% ({status})"
                    else:
                        battery_info = "Не вдалося отримати дані про батарею"

                spinner_thread = threading.Thread(target=spinner_animation, args=(stop_spinner, spinner))
                connect_thread = threading.Thread(target=connect_battery_monitor)
                monitor_thread = threading.Thread(target=monitor_battery)

                spinner_thread.start()
                connect_thread.start()

                connect_thread.join()
                spinner_thread.join()

                type_text(battery_info, Fore.YELLOW)

                monitor_thread.start()

            else:
                type_text("Моніторинг вже активний", Fore.YELLOW)
                
        elif user_input.lower() == "контроль: вимк":
            if monitoring:
                monitoring = False
                type_text("Живлення більше не під контролем", color=Fore.YELLOW)
            else:
                type_text("Моніторинг вже деактивовано", color=Fore.YELLOW)
                
        elif user_input.lower().startswith("аналіз: пам'ять"):
            sys.stdout.write(Fore.MAGENTA + "Аналізую ")
            sys.stdout.flush()

            stop_spinner = threading.Event()

            def perform_memory_analysis():
                global memory_info, disk_info
                memory_info, disk_info = get_memory_analysis()
                time.sleep(random.uniform(1, 2))
                stop_spinner.set()

            spinner_thread = threading.Thread(target=spinner_animation, args=(stop_spinner, spinner))
            analysis_thread = threading.Thread(target=perform_memory_analysis)

            spinner_thread.start()
            analysis_thread.start()

            analysis_thread.join()
            spinner_thread.join()

            sys.stdout.write('\r' + ' ' * len("Аналізую |") + '\r')
            sys.stdout.flush()

            type_text(memory_info, Fore.CYAN)
            for info in disk_info:
                type_text(info, Fore.CYAN)
                
        elif user_input.lower().startswith("аналіз: система"):
            sys.stdout.write(Fore.MAGENTA + "Аналізую ")
            sys.stdout.flush()

            stop_spinner = threading.Event()

            def perform_system_analysis():
                global system_info
                system_info = get_system_analysis()
                time.sleep(random.uniform(1, 2))
                stop_spinner.set()

            spinner_thread = threading.Thread(target=spinner_animation, args=(stop_spinner, spinner))
            analysis_thread = threading.Thread(target=perform_system_analysis)

            spinner_thread.start()
            analysis_thread.start()

            analysis_thread.join()
            spinner_thread.join()

            sys.stdout.write('\r' + ' ' * len("Аналізую |") + '\r')
            sys.stdout.flush()

            type_text(system_info, Fore.CYAN)
            
        elif user_input.lower().startswith("очистка: пам'ять"):
            sys.stdout.write(Fore.MAGENTA + "Очищаю ")
            sys.stdout.flush()

            stop_spinner = threading.Event()

            spinner_thread = threading.Thread(target=spinner_animation, args=(stop_spinner, spinner))
            spinner_thread.start()

            success, error_message = clean_temp_files()
            stop_spinner.set()
            spinner_thread.join()

            sys.stdout.write('\r' + ' ' * len("Очищаю |") + '\r')
            sys.stdout.flush()

            if success:
                type_text("Пам'ять очищена")
            else:
                type_text(f"Помилка очищення пам'яті: {error_message}")
                
        elif user_input.lower().startswith("оптимізація: енергія"):
            sys.stdout.write(Fore.MAGENTA + "Оптимізую ")
            sys.stdout.flush()

            stop_spinner = threading.Event()

            def perform_energy_optimization():
                global energy_optimization_info
                energy_optimization_info = optimize_energy_usage()
                stop_spinner.set()

            spinner_thread = threading.Thread(target=spinner_animation, args=(stop_spinner, spinner))
            optimization_thread = threading.Thread(target=perform_energy_optimization)

            spinner_thread.start()
            optimization_thread.start()

            optimization_thread.join()
            spinner_thread.join()

            sys.stdout.write('\r' + ' ' * len("Оптимізую |") + '\r')
            sys.stdout.flush()

            type_text(energy_optimization_info, Fore.CYAN)

        elif user_input.lower().startswith("аналіз: енергія"):
            sys.stdout.write(Fore.MAGENTA + "Аналізую ")
            sys.stdout.flush()

            stop_spinner = threading.Event()

            def perform_energy_analysis():
                global battery_info
                battery_info = get_energy_analysis()
                time.sleep(random.uniform(1, 2))
                stop_spinner.set()

            spinner_thread = threading.Thread(target=spinner_animation, args=(stop_spinner, spinner))
            analysis_thread = threading.Thread(target=perform_energy_analysis)

            spinner_thread.start()
            analysis_thread.start()

            analysis_thread.join()
            spinner_thread.join()

            sys.stdout.write('\r' + ' ' * len("Аналізую |") + '\r')
            sys.stdout.flush()

            type_text(battery_info, Fore.CYAN)
        
        else:
            normalized_input = preprocess_input(user_input)
            
            sys.stdout.write(Fore.MAGENTA + "Генерую ")
            sys.stdout.flush()

            stop_spinner = threading.Event()

            spinner_thread = threading.Thread(target=spinner_animation, args=(stop_spinner, spinner))
            spinner_thread.start()

            def generate_response():
                time.sleep(random.uniform(2, 3))
                stop_spinner.set()

            response_thread = threading.Thread(target=generate_response)
            response_thread.start()

            response_thread.join()
            spinner_thread.join()

            sys.stdout.write('\r' + ' ' * len("Генерую |") + '\r')
            sys.stdout.flush()

            user_vec = vectorizer.transform([normalized_input])
            distances, indices = nbrs.kneighbors(user_vec)
            closest_phrase_index = indices[0][0]

            type_text(responses[closest_phrase_index])

if __name__ == "__main__":
    main()
