#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <algorithm>
#include <cstdlib>
#include <ctime>
#include <sstream>

using namespace std;

// Structure to store a word
struct Word {
    string name;                   // The word
    string type;                   // The type of word (noun, verb, etc.)
    vector<string> definitions;    // A vector to store multiple definitions
};

// Function Prototypes
void loadDictionary(const string& filename, vector<Word>& dictionary);  
void searchWord(const vector<Word>& dictionary); 
void displayRandomWord(const vector<Word>& dictionary);
void displayMainMenu();
string getTypeAbbreviation(const string& type);

int main() {
    vector<Word> dictionary; // Vector to store words
    string filename = "dictionary_2025S1.txt";

    cout << "Welcome to the Dictionary Application...\n";
    cout << "-----------------------------------------\n";

    // Seed random number generator once
    srand(static_cast<unsigned int>(time(0)));

    // Load words from file into dictionary
    loadDictionary(filename, dictionary);

    bool isrunning = true;
    while (isrunning) {
        displayMainMenu(); // Display menu options

        string choice;
        cout << "Enter your choice (1-3): ";
        cin >> choice;
        cin.ignore(); // Prevent getline() from skipping input

        // Handle menu choices
        if (choice == "1") {
            searchWord(dictionary);
        }
        else if (choice == "2") {
            displayRandomWord(dictionary);
        }
        else if (choice == "3") {
            cout << "Thank you, Goodbye!\n";
            isrunning = false; // Exit the loop (menu)
        }
        else {
            cout << "Invalid option! Please try again.\n";
        }
    }

    return 0;
}

// Function to load words from a file into the dictionary
void loadDictionary(const string& filename, vector<Word>& dictionary) {
    ifstream file(filename);
    if (!file.is_open()) {
        cout << "Error - dictionary empty!" << endl;
        return;
    }

    string line;
    while (getline(file, line)) {
        Word word;
        word.definitions.clear();

        // Remove spaces at the beginning
        while (!line.empty() && (line[0] == ' ' || line[0] == '\t')) {
            line.erase(0, 1);
        }

        // Skip empty lines
        if (line.empty()) {
            continue;
        }

        // Process word name
        size_t semicolon_pos = line.find(';');
        if (semicolon_pos == string::npos) {
            continue;
        }
        word.name = line.substr(0, semicolon_pos);

        // Process word type
        if (!getline(file, line)) {
            break;
        }
        semicolon_pos = line.find(';');
        if (semicolon_pos == string::npos) {
            continue;
        }
        word.type = line.substr(0, semicolon_pos);

        // Process multiple definitions
        if (!getline(file, line)) {
            break;
        }

        // Split definitions using ';' as separator
        stringstream ss(line);
        string definition;
        while (getline(ss, definition, ';')) {
            if (!definition.empty()) {
                word.definitions.push_back(definition);
            }
        }

        // Add the word to the dictionary
        dictionary.push_back(word);
    }

    file.close();
    if (dictionary.empty()) {
        cout << "Dictionary loaded but its empty!\n";
    }
    else {
        cout << "Dictionary loaded Successfully!\n" << endl;
    }
}

// Function to search for a word in the dictionary
void searchWord(const vector<Word>& dictionary) {
    string input;
    cout << "\nEnter a word to search for: ";
    getline(cin, input); // Get whole line of input

    // Convert input to lowercase for case-insensitive searching
    transform(input.begin(), input.end(), input.begin(), ::tolower);

    bool found = false;
    for (const auto& word : dictionary) {
        if (word.name == input) {
            cout << "\nWord - " << word.name
                << "\nType - " << getTypeAbbreviation(word.type)
                << "\nDefinitions -\n";

            // Display each definition on a new line
            for (size_t i = 0; i < word.definitions.size(); ++i) {
                cout << "  " << (i + 1) << ". " << word.definitions[i] << endl;
            }
            cout << endl;
            found = true;
            break;
        }
    }

    if (!found) {
        cout << "Word not found.\n" << endl; // Display if the word is not found
    }
}

// Function to display a random word from the dictionary
void displayRandomWord(const vector<Word>& dictionary) {

    // Generate a random index
    int randomIndex = rand() % dictionary.size();

    // Get the random word
    const Word& word = dictionary[randomIndex];

    // Display the random word
    cout << "\nRandom Word - " << word.name
        << "\nType - " << getTypeAbbreviation(word.type)
        << "\nDefinitions -\n";

    // Print each definition on a new line
    for (size_t i = 0; i < word.definitions.size(); ++i) {
        cout << "  " << (i + 1) << ". " << word.definitions[i] << endl;
    }
    cout << endl;
}

// Function to display the main menu options
void displayMainMenu() {
    cout << "\n--------Main Menu---------" << endl;
    cout << "1. Search for a word" << endl;
    cout << "2. Display a random word" << endl;
    cout << "3. Exit" << endl;

}

// Function to return an abbreviation for a word type
string getTypeAbbreviation(const string& type) {
    if (type == "n") return "(n.)"; // Noun
    if (type == "v") return "(v.)"; // Verb
    if (type == "adv") return "(adv.)"; // Adverb
    if (type == "adj") return "(adj.)"; //Adjective
    if (type == "prep") return "(prep.)"; // Preposition
    if (type == "pn") return "(pn.)"; // ProperNoun
    if (type == "n_and_v") return "(n. v.)"; // Noun & Verb
    if (type == "misc") return "(misc.)"; // MiscWords
    return "(unknown)";
}
