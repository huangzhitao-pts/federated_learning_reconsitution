import sys, os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tensorflow_federated"))
print(sys.path)

from server import create_app


app = create_app("deployment")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8091, debug=True)
