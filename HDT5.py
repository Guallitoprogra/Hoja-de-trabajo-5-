# Importando las bibliotecas necesarias
import simpy
import random
import matplotlib.pyplot as plt

# Configuración inicial
SEED_ALEATORIA = 42
random.seed(SEED_ALEATORIA)
INSTRUCCIONES_POR_UNIDAD_CPU = 3
CAPACIDAD_RAM_INICIAL = 100
INTERVALO_GENERACION_PROCESOS = 10  # Intervalo inicial para la generación de procesos
TIEMPO_SIMULACION = 1000  # Tiempo total de simulación
NUMERO_PROCESOS = [25, 50, 100, 150, 200]  # Diferentes números de procesos para simular

# Función que simula un proceso siendo ejecutado por el sistema
def proceso(env, nombre, cpu, ram, memoria_necesaria, instrucciones):
    global tiempo_total, procesos_totales

    # Estado NUEVO: El proceso llega y solicita RAM
    tiempo_llegada = env.now
    print(f'{env.now:.2f} Proceso {nombre}: Nuevo - Solicitando {memoria_necesaria} unidades de RAM')
    with ram.get(memoria_necesaria) as solicitud:
        yield solicitud

        # Estado LISTO: Proceso obtuvo RAM y ahora espera CPU
        print(f'{env.now:.2f} Proceso {nombre}: Listo - Esperando CPU')
        with cpu.request() as req:
            yield req

            # Estado EJECUTANDO: Proceso usa el CPU
            print(f'{env.now:.2f} Proceso {nombre}: Ejecutando')
            instrucciones_restantes = instrucciones
            while instrucciones_restantes > 0:
                yield env.timeout(1)  # Simula el paso del tiempo mientras el proceso usa el CPU
                instrucciones_restantes -= INSTRUCCIONES_POR_UNIDAD_CPU
                print(f'{env.now:.2f} Proceso {nombre}: {max(instrucciones_restantes, 0)} instrucciones restantes')

            # Proceso termina y libera recursos
            print(f'{env.now:.2f} Proceso {nombre}: Terminado')
            ram.put(memoria_necesaria)  # Libera RAM
            tiempo_total += env.now - tiempo_llegada
            procesos_totales += 1

# Función para generar procesos en intervalos aleatorios
def generador_procesos(env, cpu, ram):
    for i in range(max(NUMERO_PROCESOS)):
        memoria_necesaria = random.randint(1, 10)  # Memoria necesaria para el proceso
        instrucciones = random.randint(1, 10)  # Total de instrucciones del proceso
        env.process(proceso(env, f'Proceso {i}', cpu, ram, memoria_necesaria, instrucciones))
        t = random.expovariate(1.0 / INTERVALO_GENERACION_PROCESOS)
        yield env.timeout(t)

# Función para ejecutar la simulación
def ejecutar_simulacion(num_procesos, intervalo_gen_proceso):
    global tiempo_total, procesos_totales
    tiempo_total = 0
    procesos_totales = 0
    env = simpy.Environment()
    cpu = simpy.Resource(env, capacity=1)  # Recurso CPU
    ram = simpy.Container(env, init=CAPACIDAD_RAM_INICIAL, capacity=CAPACIDAD_RAM_INICIAL)  # Recurso RAM
    env.process(generador_procesos(env, cpu, ram))
    env.run(until=TIEMPO_SIMULACION)

    # Calcula y retorna el tiempo medio en el sistema
    tiempo_medio = tiempo_total / procesos_totales if procesos_totales else 0
    return tiempo_medio

# Lógica principal de simulación
tiempos_medios = []
for n in NUMERO_PROCESOS:
    INTERVALO_GENERACION_PROCESOS = 10  # Reinicia el intervalo para cada ejecución
    tiempo_medio = ejecutar_simulacion(n, INTERVALO_GENERACION_PROCESOS)
    tiempos_medios.append(tiempo_medio)

# Graficando los resultados
plt.figure(figsize=(10, 6))
plt.plot(NUMERO_PROCESOS, tiempos_medios, marker='o')
plt.title('Tiempo Medio de los Procesos en el Sistema')
plt.xlabel('Número de Procesos')
plt.ylabel('Tiempo Medio en el Sistema')
plt.grid(True)
plt.show()