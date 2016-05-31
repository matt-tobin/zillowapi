
import optparse

def zillowrun(app):
    """
    Takes a flask.Flask instance and runs it. Parses
    command-line flags to configure the app.
    """
    parser = optparse.OptionParser()
    parser.add_option("-k", "--key",
                      help="Zillow Web Services ID Key")
    options, _ = parser.parse_args()
    app.config['ZKEY'] = options.key
    app.run()