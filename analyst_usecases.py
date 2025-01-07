from models.analyst import Analyst
from config import BASE_URL_QUERY_HYPNO, BASE_URL_QUERY_DNA

def hypnogram_case():
    analyst = Analyst("Seppo")
    hypno_query_value = 7
    user_id_query = 1
    hypno_response = analyst.query_data(user_id_query, hypno_query_value, BASE_URL_QUERY_HYPNO)

    hypno_count = analyst.count_the_value(hypno_response)
    print(f"Count for value {hypno_query_value}: {hypno_count}")

    hypno_transitions = analyst.count_transitions(hypno_response)
    print(f"Amount of transitions for value {hypno_query_value}: {hypno_transitions}")

    hypno_sequense = analyst.count_sequences(hypno_response)
    print(f"Amount of sequences for value {hypno_query_value}: {hypno_sequense}")

def dna_case():
    analyst = Analyst("Harri")
    dna_query_value = "AG"
    user_id_query = 13
    dna_response = analyst.query_data(user_id_query, dna_query_value, BASE_URL_QUERY_DNA)

    dna_count = analyst.count_the_value(dna_response)
    print(f"Count for value {dna_query_value}: {dna_count}")

    dna_transitions = analyst.count_transitions(dna_response)
    print(f"Amount of transitions for value {dna_query_value}: {dna_transitions}")

    dna_sequense = analyst.count_sequences(dna_response)
    print(f"Amount of sequences for value {dna_query_value}: {dna_sequense}")

def inser_data():
    data = {}

if __name__ == '__main__':
    hypnogram_case()
    dna_case()