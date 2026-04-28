from beam_analyzer import BeamAnalyzer

Folder_address82 = r'F:\Users\GENERAL\TEMP\Behrad\*\Hex2GRIN\acquisition\acquisituin_pupil\4-27-26 re-terminated\POINTING\340101-2\82-newjig'
#Folder_address235 = r'F:\Users\GENERAL\TEMP\Behrad\*\Hex2GRIN\acquisition\acquisituin_pupil\4-27-26 re-terminated\POINTING\340101-2\235'

analyzer82=BeamAnalyzer(Folder_address82)
#analyzer235=BeamAnalyzer(Folder_address235)

analyzer82.find_images()
#analyzer235.find_images()

analyzer82.process_beams()
#analyzer235.process_beams()

analyzer82.save_visuals()
#analyzer235.save_visuals()



print('\n---Final Results---')
for res in analyzer82.results:
    print(f"file: {res['filename']}")
    print(f"\n Center:{res['center']}")
    print(f"\n Radius:{res['radius']}")
#for res in analyzer235.results:
    print(f"file: {res['filename']}")
    print(f"\n Center:{res['center']}")
    print(f"\n Radius:{res['radius']}")


analyzer82.analyze_groups() 
#analyzer235.analyze_groups()


analyzer82.Pointing()
#analyzer235.Pointing()

analyzer82.save_to_csv("analysis_results.csv")
#analyzer235.save_to_csv("analysis_results.csv")