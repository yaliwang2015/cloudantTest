import requests
import json

class CloudantTester:
    uid = 'yaliwang2015'
    pwd = 'interview'

    # create db status code
    create_db_status = {201:"Database created successfully",
                        202:"The database has been successfully created on some nodes, but the number of nodes is less than the write quorum.",
                        403:"Invalid database name.",
                        400:"Ilegal database name",
                        412:"Database aleady exists."}

    # headers for document
    doc_headers={"content-type":"application/json"}

    def __init__(self, userid=None, password=None, url='cloudant.com'):
        if password is None:
            self.password = self.pwd
        else:
            self.password = password

        if userid is None:
            self.userid = self.uid
        else:
            self.userid = userid

        self.auth = (self.userid, self.password)

        self.cloudant_url = "{0}{1}.{2}/".format("https://", self.userid, url)


    def create_db(self, dbname):
        """
        The database name must start with a lowercase letter and contain only the following characters:
        Lowercase characters (a-z)
        Digits (0-9)
        Any of the characters _, $, (, ), +, -, and /
        :param dbname:
        :return:
        """
        this_db_request = self.cloudant_url + dbname
        # create db by sending this request to cloudant
        response = requests.put(this_db_request, auth=self.auth)
        return response

    def describe_response(self, response):
        # check the response code
        """
        201	Database created successfully
        202	The database has been successfully created on some nodes, but the number of nodes is less than the write quorum.
        403	Invalid database name.
        412	Database aleady exists.
        """
        result = "{0} method={1} status_code={2} reason={3}".format(response.url, response.request.method,
                                                                    response.status_code,
                                                                    self.create_db_status[response.status_code])
        return result

    def test_create_db(self):
        dbname = 'test_create_db_1'
        bad_dbname = 'TESTDB'
        # first try to delete this db if it exists already
        # compare with creating db, delete db 10 times slower from my test result
        rp = requests.delete(self.cloudant_url + dbname, auth=self.auth)
        print "Delete DB status_code={0}, reason: {1}".format(rp.status_code, rp.reason)
        if rp.status_code!=200 and rp.status_code!=404:
            return

        # test create a new db, 201 response code is expected
        rp = self.create_db(dbname)

        print "test create new db:", self.describe_response(rp)
        if rp.status_code == 201:
            print "test 201 status code: succeed"
        else:
            print "test 201 status code: fail"


        # test create db if db exists, 412 response code is expected
        rp = self.create_db(dbname)
        print "test create db which exists:", self.describe_response(rp)
        if rp.status_code == 412:
            print "test 412 status code: succeed"
        else:
            print "test 412 status code: fail"

        rp = self.create_db(bad_dbname)
        print "test create db with bad db name:", self.describe_response(rp)
        # Document mention 403 should be the returned status code for the invalid database name,
        # however, the code returned 400 instead of 403
        if rp.status_code == 400:
            print "test 400 status code: succeed"
        else:
            print "test 400 status code: fail"

    def create_document(self, dbname, docname):
        this_doc_request = self.cloudant_url + dbname + "/" + docname
        rp = requests.put(this_doc_request,
             auth=self.auth,
             headers=self.doc_headers,
             data=json.dumps({"foo":"bar"}))
        return rp

    def test_create_doc(self, dbname, docname):
        # make sure DB exists
        rp = self.create_db(dbname)
        if rp.status_code != 201 and rp.status_code != 412:
            print "Create DB failed, dbname=" + dbname
            return

        # create document
        rp = self.create_document(dbname, docname)
        rp_result = "{0} method={1} status_code={2} reason={3}".format(rp.url, rp.request.method,
                                                                       rp.status_code,
                                                                       rp.reason)

         # test create a new document, 201 response code is expected
        print "test create new document:", rp_result
        if rp.status_code == 201:
            print "test 201 status code: succeed"
        else:
            print "test 201 status code: fail"

        # test if we can get back the same document
        rp = requests.get(self.cloudant_url + dbname + "/" + docname, auth=self.auth)
        doc= json.loads(rp.content)

        if doc["foo"] == "bar" and doc["_id"] == docname:
            print "Document retrivel succeed"
        return None



tester = CloudantTester()
tester.test_create_db()
tester.test_create_doc("test_create_db_1", "classmate")

