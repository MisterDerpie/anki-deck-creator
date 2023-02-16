#!/bin/python3
from genanki import Model, Deck, Note, Package, guid_for
import json
import sys

MAX_SIGNED_INT = 2147483647

if len(sys.argv) == 1:
    print("Please specify exactly one parameter, the input file. See README for example.")
    exit(1)

input_file = sys.argv[1]
input_json = json.load(open(input_file))

language_from = input_json["from"]
language_to = input_json["to"]
deck_name = input_json["name"]
words = input_json["words"]

deck_hash = hash(deck_name) % MAX_SIGNED_INT

class NoteWithCustomHash(Note):
  @property
  def guid(self):
    return guid_for(self.fields[0] + str(deck_hash) , self.fields[1] + str(deck_hash))

anki_model = Model(
    20230212,
    'AnkieDeckModel',
    fields = [
        {'name': language_from},
        {'name': language_to}
    ],
    templates = [
        {
            'name': 'Card',
            'qfmt': '<center><h2>{{' + language_from + '}}</h2></center>',
            'afmt': """
            {{FrontSide}}
            <hr id="answer"/>
            <center><h2>{{""" + language_to +"""}}</h2></center>""".strip()
        }
    ]
)

anki_deck = Deck(
    deck_hash,
    deck_name
)

def add_note(language_from: str, language_to: str, model: Model, deck: Deck) -> None:
    deck.add_note(
        NoteWithCustomHash(
            model = model,
            fields = [language_from, language_to]
        )
    )

for word in words:
    add_note(
        language_from = word[language_from],
        language_to = word[language_to],
        model = anki_model,
        deck = anki_deck
    )

output_file = input_file + ".apkg"
Package(anki_deck).write_to_file(output_file)