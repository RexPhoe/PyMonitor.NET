#!/usr/bin/env python3
"""
Ejemplo de uso de la funcionalidad de CPU Frequency en PyMonitor.NET

Este script demuestra cómo el monitor de hardware calcula y muestra
la frecuencia máxima del procesador en tiempo real.
"""

import sys
import os
import time

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from pymonitor.hardware.monitor import HardwareMonitor
from pymonitor.config.settings import Settings


def demo_cpu_frequency_monitoring():
    """
    Demuestra el monitoreo de frecuencia de CPU en tiempo real
    """
    print("=== PyMonitor.NET - Demo de Monitoreo de Frecuencia CPU ===\n")

    try:
        # Configurar el monitor
        settings = Settings("settings.json")
        monitor = HardwareMonitor(settings, lib_path=".")

        print("🔧 Inicializando monitor de hardware...")
        print(
            "⚠️  Nota: Se requieren privilegios de administrador para acceso completo al hardware\n"
        )

        monitor.initialize()

        print("📊 Monitoreando frecuencia del CPU por 30 segundos...")
        print("⏱️  Actualizando cada 2 segundos...\n")
        print("-" * 60)

        for i in range(15):  # 30 segundos total
            data = monitor.get_hardware_data()

            # Buscar datos del CPU
            cpu_data = None
            for hardware in data:
                if "cpu" in hardware["name"].lower() or hardware["type"] == "Cpu":
                    cpu_data = hardware
                    break

            if cpu_data:
                # Buscar el sensor de CPU Frequency
                cpu_freq_sensor = None
                core_frequencies = []

                for sensor in cpu_data["sensors"]:
                    if sensor["name"] == "CPU Frequency":
                        cpu_freq_sensor = sensor
                    elif "Core" in sensor["name"] and sensor["type"] == "Clock":
                        # Extraer valor numérico de frecuencia
                        try:
                            freq_str = sensor["value"].split()[0]
                            freq_value = float(freq_str)
                            core_frequencies.append((sensor["name"], freq_value))
                        except:
                            pass

                # Mostrar información
                timestamp = time.strftime("%H:%M:%S")
                print(f"[{timestamp}] CPU: {cpu_data['name']}")

                if cpu_freq_sensor:
                    print(f"  🚀 Frecuencia Máxima: {cpu_freq_sensor['value']}")
                else:
                    print("  ❌ Sensor 'CPU Frequency' no encontrado")

                if core_frequencies:
                    print(f"  🔢 Núcleos activos: {len(core_frequencies)}")
                    # Mostrar solo algunos núcleos para no saturar la pantalla
                    for name, freq in core_frequencies[:4]:
                        print(f"     {name}: {freq:.2f} MHz")
                    if len(core_frequencies) > 4:
                        print(f"     ... y {len(core_frequencies) - 4} núcleos más")

                print("-" * 60)
            else:
                print(
                    f"[{time.strftime('%H:%M:%S')}] ❌ No se encontraron datos del CPU"
                )

            time.sleep(2)

        print("\n✅ Demo completada!")
        monitor.close()

    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrumpida por el usuario")
        if "monitor" in locals():
            monitor.close()

    except Exception as e:
        print(f"\n❌ Error durante la demo: {e}")
        print("\n💡 Consejos para solucionar problemas:")
        print("   1. Ejecutar como administrador")
        print("   2. Verificar que LibreHardwareMonitorLib.dll esté presente")
        print("   3. Verificar que .NET 8+ esté instalado")


if __name__ == "__main__":
    demo_cpu_frequency_monitoring()
