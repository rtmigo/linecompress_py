from chkpkg import Package

if __name__ == "__main__":
    with Package() as pkg:
        pkg.run_python_code('from spacy_installer import load_model,'
                            ' install_model, uninstall_model,'
                            ' uninstall_all_models, can_load')

    print("\nPackage is OK!")

