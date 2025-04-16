OBTAIN voice lista
python component_test/elevenlabs/voice_list.py

TEST ElevenLabs
python component_test/elevenlabs/test_eleven_labs.py


TEST rhubarb with phonetic
python component_test/rhubarb/test_rhubarb_with_phonetic.py component_test/elevenlabs/test_output/test_italian_complex.mp3 --output component_test/rhubarb/test_output/output_phon.json

TEST rhubarn with PocketSphinx
python component_test/rhubarb/test_rhubarb.py component_test/elevenlabs/test_output/test_italian_complex.mp3 --output component_test/rhubarb/test_output/output_pock.json
