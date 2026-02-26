from beam_analyzer import BeamAnalyzer

Folder_address82 = r'F:\Users\GENERAL\TEMP\Behrad\ASML\Hex2GRIN\Python\Pointing\82'
Folder_address235 = r'F:\Users\GENERAL\TEMP\Behrad\ASML\Hex2GRIN\Python\Pointing\235'

analyzer82=BeamAnalyzer(Folder_address82)
analyzer235=BeamAnalyzer(Folder_address235)

analyzer82.find_images()

analyzer82.process_beams()

# analyzer82.save_visuals()



print('\n---Final Results---')
for res in analyzer82.results:
    print(f"file: {res['filename']}")
    print(f"\n Center:{res['center']}")
    print(f"\n Radius:{res['radius']}")


analyzer82.analyze_groups(700) #value is something inbetween the radius in Z1 and Z2 positions

analyzer82.Pointing(700)