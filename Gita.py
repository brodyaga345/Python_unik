import time
import os
import json

# --- Конфігурація для GitHub ---
REPO_OWNER = "Andrij210"  # Замініть на ваше ім'я користувача GitHub
REPO_NAME = "eco_sim"  # Назва вашого репозиторію
DATA_FILE = "ecosystem_data.json"

def save_data_to_github(data, commit_message="Оновлення даних екосистеми"):
    try:
        from github import Github

        # Переконайтеся, що у вас є токен GitHub як змінна середовища
        github_token = os.environ.get("GITHUB_TOKEN")
        if not github_token:
            print("Помилка: Не знайдено токен GitHub у змінних середовища.")
            return False

        g = Github(github_token)
        repo = g.get_user(REPO_OWNER).get_repo(REPO_NAME)
        contents = repo.get_contents(DATA_FILE, ref="main")  # Або ваша основна гілка

        repo.update_file(
            path=DATA_FILE,
            message=commit_message,
            content=json.dumps(data, indent=4),
            sha=contents.sha,
            branch="main"  # Або ваша основна гілка
        )
        print(f"Дані екосистеми збережено на GitHub у файлі {DATA_FILE}")
        return True
    except Exception as e:
        print(f"Помилка збереження даних на GitHub: {e}")
        return False

def load_data_from_github():
    try:
        from github import Github

        github_token = os.environ.get("GITHUB_TOKEN")
        if not github_token:
            print("Помилка: Не знайдено токен GitHub у змінних середовища.")
            return {}

        g = Github(github_token)
        repo = g.get_user(REPO_OWNER).get_repo(REPO_NAME)
        contents = repo.get_contents(DATA_FILE, ref="main")
        return json.loads(contents.decoded_content.decode('utf-8'))
    except Exception as e:
        print(f"Помилка завантаження даних з GitHub: {e}")
        return {}

# --- Абстрактний клас Species ---
class Species:
    def init(self, name, energy_needs=1, reproduction_rate=0.1):
        self.name = name
        self.energy_needs = energy_needs
        self.reproduction_rate = reproduction_rate
        self.population = 0

    def reproduce(self):
        if random.random() < self.reproduction_rate:
            self.population += 1

    def consume_energy(self):
        if self.population > 0:
            energy_consumed = self.population * self.energy_needs
            return energy_consumed
        return 0

    def str(self):
        return f"{self.name} (Популяція: {self.population})"

# --- Підкласи Species ---
class Plant(Species):
    def init(self, name, energy_production=2, reproduction_rate=0.05):
        super().init(name, energy_needs=0, reproduction_rate=reproduction_rate)
        self.energy_production = energy_production

    def produce_energy(self):
        return self.population * self.energy_production

class Animal(Species):
    def init(self, name, energy_needs=2, prey=None, reproduction_rate=0.08):
        super().init(name, energy_needs, reproduction_rate)
        self.prey = prey if prey else []

    def hunt(self, environment):
        if self.population > 0 and self.prey and environment.species:
            available_prey = [s for s in environment.species if s.name in self.prey and s.population > 0]
            if available_prey:
                target_prey = random.choice(available_prey)
                if target_prey.population > 0:
                    target_prey.population -= 1
                    return self.energy_needs  # Отримує енергію від полювання
        return 0

    def init(self, name, decomposition_rate=0.2, reproduction_rate=0.15):
        super().init(name, energy_needs=0.5, reproduction_rate=reproduction_rate)
        self.decomposition_rate = decomposition_rate

    def decompose(self, environment):
        # Проста модель: випадково збільшує ресурси середовища
        if self.population > 0 and random.random() < self.decomposition_rate:
            environment.resources += self.population * 0.1
            return self.population * 0.05  # Споживає трохи ресурсів
        return 0


# --- Клас Environment ---
class Environment:
    def init(self, name, climate="помірний", resources=100):
        self.name = name
        self.climate = climate
        self.resources = resources
        self.species = []

    def introduce_species(self, species):
        self.species.append(species)
        print(f"До екосистеми '{self.name}' додано вид: {species.name}")

    def simulate_interactions(self):
        print(f"\n--- Симуляція взаємодій в екосистемі '{self.name}' ---")
        for species in self.species:
            species.reproduce()
            energy_consumed = species.consume_energy()
            self.resources -= energy_consumed
            if isinstance(species, Plant):
                energy_produced = species.produce_energy()
                self.resources += energy_produced
                print(f"{species.name} виробило {energy_produced:.2f} енергії.")
            elif isinstance(species, Animal):
                energy_gained = species.hunt(self)
                self.resources -= energy_gained  # Полювання може призвести до втрати енергії для середовища (якщо жертву забирають)
                print(
                    f"{species.name} спожило {energy_consumed:.2f} енергії, полювало та отримало {energy_gained:.2f} енергії.")
            elif isinstance(species, Microorganism):
                energy_consumed = species.consume_energy()
                resources_gained = species.decompose(self)
                self.resources += resources_gained
                self.resources -= energy_consumed
                print(
                    f"{species.name} спожило {energy_consumed:.2f} енергії та розклало, додавши {resources_gained:.2f} ресурсів.")
            print(species)
        print(f"Залишок ресурсів: {self.resources:.2f}")

    def adjust_climate(self, new_climate):
        print(f"Клімат в '{self.name}' змінено з '{self.climate}' на '{new_climate}'.")
        self.climate = new_climate
        # Вплив клімату можна додати в майбутньому (наприклад, на швидкість розмноження)

    def monitor_biodiversity(self):
        num_species = len(self.species)
        total_population = sum(s.population for s in self.species)
        print(f"\n--- Моніторинг біорізноманіття в '{self.name}' ---")
        print(f"Кількість видів: {num_species}")
        print(f"Загальна популяція: {total_population}")
# Дуже проста спроба балансування: регулювання популяції на основі ресурсів
        capacity = self.resources / 10  # Приблизна місткість екосистеми
        for species in self.species:
            if species.population > capacity * 2:
                reduction = int(species.population * 0.1)
                species.population -= reduction
                print(f"Популяція {species.name} зменшена на {reduction} для балансування.")
            elif species.population < capacity * 0.1 and capacity > 10:
                increase = int(capacity * 0.05)
                species.population += increase
                print(f"Популяція {species.name} збільшена на {increase}.")

# --- Основна частина симуляції ---
def main():
    ecosystem_data = load_data_from_github()
    environments = {}

    if ecosystem_data and "environments" in ecosystem_data:
        print("Завантажено існуючі екосистеми з GitHub.")
        for env_name, env_data in ecosystem_data["environments"].items():
            env = Environment(env_name, env_data.get("climate", "помірний"), env_data.get("resources", 100))
            for species_data in env_data.get("species", []):
                species_type = species_data.get("type")
                name = species_data.get("name")
                population = species_data.get("population", 0)
                energy_needs = species_data.get("energy_needs", 1)
                reproduction_rate = species_data.get("reproduction_rate", 0.1)
                energy_production = species_data.get("energy_production", 2)
                prey = species_data.get("prey")
                decomposition_rate = species_data.get("decomposition_rate", 0.2)

                if species_type == "Plant":
                    plant = Plant(name, energy_production, reproduction_rate)
                    plant.population = population
                    env.introduce_species(plant)
                elif species_type == "Animal":
                    animal = Animal(name, energy_needs, prey, reproduction_rate)
                    animal.population = population
                    env.introduce_species(animal)
                elif species_type == "Microorganism":
                    micro = Microorganism(name, decomposition_rate, reproduction_rate)
                    micro.population = population
                    env.introduce_species(micro)
            environments[env_name] = env
    else:
        print("Створення нової екосистеми...")
        earth = Environment("Земля", resources=200)
        sunflower = Plant("Соняшник")
        rabbit = Animal("Кролик", prey=["Соняшник"])
        fox = Animal("Лисиця", prey=["Кролик"])
        bacteria = Microorganism("Бактерії")

        earth.introduce_species(sunflower)
        earth.introduce_species(rabbit)
        earth.introduce_species(fox)
        earth.introduce_species(bacteria)

        sunflower.population = 50
        rabbit.population = 20
        fox.population = 5
        bacteria.population = 100

        environments["Земля"] = earth
for env_name, env in environments.items():
            print(f"\n--- Етап {i+1} для екосистеми '{env_name}' ---")
            env.simulate_interactions()
            env.monitor_biodiversity()
            env.balance_ecosystem()
            time.sleep(1)

        # Збереження даних після кожного етапу
        data_to_save = {"environments": {}}
        for env_name, env in environments.items():
            env_data = {
                "climate": env.climate,
                "resources": env.resources,
                "species": []
            }
            for species in env.species:
                species_data = {"type": species.class.name, "name": species.name, "population": species.population}
                if isinstance(species, Plant):
                    species_data["energy_production"] = species.energy_production
                elif isinstance(species, Animal):
                    species_data["energy_needs"] = species.energy_needs
                    species_data["prey"] = species.prey
                    species_data["reproduction_rate"] = species.reproduction_rate
                elif isinstance(species, Microorganism):
                    species_data["decomposition_rate"] = species.decomposition_rate
                    species_data["reproduction_rate"] = species.reproduction_rate
                    species_data["energy_needs"] = species.energy_needs
                env_data["species"].append(species_data)
            data_to_save["environments"][env_name] = env_data
        save_data_to_github(data_to_save, f"Автоматичне збереження екосистеми - Етап {i+1}")

if name == "main":
    main()
