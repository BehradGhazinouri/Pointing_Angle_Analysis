from beam_analyzer import BeamAnalyzer

Folder_address82 = r'C:\Users\bghazinouri\Documents\Pointing\82'
Folder_address235 = r'C:\Users\bghazinouri\Documents\Pointing\235'

analyzer82=BeamAnalyzer(Folder_address82)
analyzer235=BeamAnalyzer(Folder_address235)

analyzer82.find_images()
analyzer235.find_images()

analyzer82.process_beams()
analyzer235.process_beams()

analyzer82.save_visuals()
analyzer235.save_visuals()



print('\n---Final Results---')
for res in analyzer82.results:
    print(f"file: {res['filename']}")
    print(f"\n Center:{res['center']}")
    print(f"\n Radius:{res['radius']}")
for res in analyzer235.results:
    print(f"file: {res['filename']}")
    print(f"\n Center:{res['center']}")
    print(f"\n Radius:{res['radius']}")


analyzer82.analyze_groups(700) #value is something inbetween the radius in Z1 and Z2 positions
analyzer235.analyze_groups(700)


analyzer82.Pointing(700)
analyzer235.Pointing(700)