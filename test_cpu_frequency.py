#!/usr/bin/env python3
"""
Script de prueba para verificar que la funcionalidad de CPU Frequency está funcionando correctamente
"""

import sys
import os

# Agregar el directorio src al path para poder importar los módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from pymonitor.hardware.monitor import HardwareMonitor
from pymonitor.config.settings import Settings


def test_cpu_frequency():
    """Prueba la funcionalidad de CPU Frequency"""
    try:
        # Inicializar settings y monitor
        settings = Settings("settings.json")
        monitor = HardwareMonitor(settings, lib_path=".")

        print("Inicializando monitor de hardware...")
        monitor.initialize()

        print("Obteniendo datos de hardware...")
        data = monitor.get_hardware_data()

        # Buscar datos del CPU
        cpu_data = None
        for hardware in data:
            if "cpu" in hardware["name"].lower() or hardware["type"] == "Cpu":
                cpu_data = hardware
                break

        if cpu_data:
            print(f"\n=== CPU: {cpu_data['name']} ===")
            print(f"Tipo: {cpu_data['type']}")
            print("\nSensores disponibles:")

            cpu_frequency_found = False
            for sensor in cpu_data["sensors"]:
                print(
                    f"  - {sensor['name']}: {sensor['value']} (Tipo: {sensor['type']})"
                )
                if sensor["name"] == "CPU Frequency":
                    cpu_frequency_found = True
                    print(f"    ✅ CPU Frequency detectada: {sensor['value']}")

            if cpu_frequency_found:
                print(
                    "\n✅ ¡La funcionalidad de CPU Frequency está funcionando correctamente!"
                )
            else:
                print("\n❌ No se encontró el sensor 'CPU Frequency'")
                print("Verificando sensores de reloj de núcleos...")

                clock_sensors = [
                    s
                    for s in cpu_data["sensors"]
                    if s["type"] == "Clock" and "Core" in s["name"]
                ]
                if clock_sensors:
                    print(f"Sensores de reloj encontrados: {len(clock_sensors)}")
                    for sensor in clock_sensors:
                        print(f"  - {sensor['name']}: {sensor['value']}")
                else:
                    print("No se encontraron sensores de reloj de núcleos")
        else:
            print("❌ No se encontraron datos del CPU")

        # Cerrar el monitor
        monitor.close()

    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_cpu_frequency()
