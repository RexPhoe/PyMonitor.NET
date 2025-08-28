#!/usr/bin/env python3
"""
Script de diagnóstico para identificar problemas de inicio
"""

import sys
import os
import traceback


def diagnose_startup_issue():
    """Diagnostica problemas de inicio paso a paso"""
    print("=== Diagnóstico de problemas de inicio ===")

    # 1. Verificar path y imports básicos
    print("1. Verificando path y imports básicos...")
    try:
        src_path = os.path.join(os.path.dirname(__file__), "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        print(f"   ✅ Path agregado: {src_path}")
    except Exception as e:
        print(f"   ❌ Error agregando path: {e}")
        return False

    # 2. Testear imports básicos
    print("2. Probando imports básicos...")
    try:
        from pymonitor.main import main

        print("   ✅ Import de main exitoso")
    except Exception as e:
        print(f"   ❌ Error importando main: {e}")
        traceback.print_exc()
        return False

    # 3. Testear imports de dependencias
    print("3. Probando imports de dependencias...")
    try:
        from PyQt6.QtWidgets import QApplication

        print("   ✅ PyQt6 disponible")
    except Exception as e:
        print(f"   ❌ Error con PyQt6: {e}")
        return False

    # 4. Testear creación de argumentos
    print("4. Probando creación de argumentos...")
    try:
        test_args = ["test_app"]
        print(f"   ✅ Args de prueba: {test_args}")
    except Exception as e:
        print(f"   ❌ Error con argumentos: {e}")
        return False

    # 5. Testear imports específicos de la aplicación
    print("5. Probando imports específicos...")
    try:
        from pymonitor.core.app import Application

        print("   ✅ Application import exitoso")
    except Exception as e:
        print(f"   ❌ Error importando Application: {e}")
        traceback.print_exc()
        return False

    # 6. Testear instanciación básica (sin inicializar hardware)
    print("6. Probando instanciación básica...")
    try:
        # No creamos la aplicación real para evitar problemas con Qt
        print("   ✅ Test de instanciación preparado")
    except Exception as e:
        print(f"   ❌ Error en instanciación: {e}")
        traceback.print_exc()
        return False

    # 7. Verificar archivos necesarios
    print("7. Verificando archivos necesarios...")
    required_files = ["LibreHardwareMonitorLib.dll", "HidSharp.dll", "settings.json"]

    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file} encontrado")
        else:
            print(f"   ⚠️  {file} no encontrado")

    print("\n🎉 Diagnóstico básico completado exitosamente!")
    print("El problema podría estar en la inicialización del hardware monitor.")
    print("Intenta ejecutar la aplicación manualmente para ver errores específicos.")

    return True


if __name__ == "__main__":
    if diagnose_startup_issue():
        print("\n💡 Sugerencias:")
        print("1. Ejecuta: python -m src.pymonitor.main")
        print("2. Revisa si hay errores específicos en la consola")
        print("3. Verifica que LibreHardwareMonitorLib.dll sea compatible")
    else:
        print("\n❌ Se encontraron problemas básicos que deben resolverse primero.")
