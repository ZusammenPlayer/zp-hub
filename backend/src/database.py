import copy
import json
import os
import random
from slugify import slugify
import string
import logging


class DatabaseException(Exception):
    """Exception raised when a database error occurs

    Attributes:
        code -- error code
        message -- error message
    """

    def __init__(self, code, message="A database error occured"):
        self.code = code
        self.message = message
        super().__init__(self.message)

    def to_json(self):
        err = {"code": self.code, "message": self.message}
        return json.dumps(err)


class Database:
    """Simple database abstraction providing access and manipulation of
    ZP data that need to be persisted. This implementation usees simple
    json files and automatically - if available - takes care of versioning
    using git.
    The Database creates a file called `db.json` and for each project a file
    in the `projects` folder.

    Attributes:
        data_dir -- path to a directory where data will be stored
    """

    def __init__(self, data_dir):
        self.__DB = None
        self.__data_dir = data_dir
        self.__db_file_path = data_dir + "/db.json"
        self.__projects_dir = data_dir + "/projects"

    def init(self):
        """
        Loads data from database file. If it does not exist
        it will be created.

        Raises
        ------
        DatabaseException
            if specified data_dir is not a directory or if
            existing database is not a file.
        """
        # check if data path exists, otherwise create it
        if not os.path.exists(self.__data_dir):
            os.mkdir(self.__data_dir)
            logging.info("created zp data directory")

        # check if projects directory exists otherwise create one
        if not os.path.exists(self.__projects_dir):
            os.mkdir(self.__projects_dir)
            logging.info("created zp projects directory")

        # check if database file exists otherwise create one
        if not os.path.exists(self.__db_file_path):
            with open(self.__db_file_path, "w") as outfile:
                self.__DB = {"version": 1, "projects": [], "devices": []}
                outfile.write(json.dumps(self.__DB))
                logging.info("zp-database file created")

        # check if data file is a file
        if not os.path.isfile(self.__db_file_path):
            raise DatabaseException(1, "database file is a directory")

        # check if project dir is a directory
        if not os.path.isdir(self.__projects_dir):
            raise DatabaseException(
                2, "projects path is a file but should be a directory"
            )
        
        # load database
        with open(self.__db_file_path) as db:
            self.__DB = json.load(db)
            if "devices" not in self.__DB:
                self.__DB["devices"] = []
                self.__save_database()
            if "projects" not in self.__DB:
                self.__DB["projects"] = []
                self.__save_database()

    def create_new_project(self, data):
        """
        Creates a new project in the database. Projects metadata are added to
        the database file and a new file for the project data itself is created
        in the projects folder

        Raises
        ------
        DatabaseException
            if a project with the specified name already exists
        """
        # check wether a project with the specified name already exists
        project_name_exists = False
        for project in self.__DB["projects"]:
            if project["name"] == data["name"]:
                project_name_exists = True

        if project_name_exists:
            raise DatabaseException(3, "project with given name already exists")
        else:
            slug = slugify(data["name"])
            id = "project_" + "".join(
                random.choices(string.ascii_letters + string.digits, k=10)
            )
            file_name = self.__projects_dir + "/" + id + ".json"

            new_project = {
                "id": id,
                "name": data["name"],
                "slug": slug,
                "file_name": file_name,
                "scenes": [],
                "virtual_devices": [],
                "cuelists": [],
                "media": []
            }

            # save project meta data to db
            self.__DB["projects"].append(new_project)
            self.__save_database()

            # save project data to file (remove file_name first)
            project_data = copy.deepcopy(new_project)
            del project_data["file_name"]
            out = json.dumps(project_data)
            with open(file_name, "w") as outfile:
                outfile.write(out)
            return project_data

    def get_projects(self):
        # we don't want to expose the file name where project data are stored
        # so this property is removed from the object after a deep copy is made
        projects = []
        for p in self.__DB["projects"]:
            p_min = copy.deepcopy(p)
            del p_min["file_name"]
            projects.append(p_min)
        return projects

    def get_project(self, id):
        for project in self.__DB["projects"]:
            if project["id"] == id:
                if os.path.exists(project["file_name"]):
                    with open(project["file_name"], "r") as outfile:
                        return json.load(outfile)
                else:
                    return None
        return None

    def get_project_by_slug(self, slug):
        for project in self.__DB["projects"]:
            if project["slug"] == slug:
                return self.get_project(project["id"])
        return None

    def delete_project(self, id):
        project = self.get_project(id)
        if project is not None:
            if os.path.exists(project["file_name"]):
                os.remove(project["file_name"])
        self.__DB["projects"] = [p for p in self.__DB["projects"] if p["id"] == id]
        self.__save_database()

    def save_project(self, project):
        id = project["id"]
        file_name = self.__projects_dir + "/" + id + ".json"
        out = json.dumps(project)
        with open(file_name, "w") as f:
            f.write(out)
        return project
    
    def get_devices(self):
        return self.__DB["devices"]

    def add_or_update_device(self, device):
        devices = self.__DB["devices"] = [d for d in self.__DB["devices"] if d["uid"] != device["uid"]]
        devices.append(device)
        self.__DB["devices"] = devices
        self.__save_database()

    def remove_device(self, device_id):
        self.__DB["devices"] = [d for d in self.__DB["devices"] if d["uid"] == id]
        self.__save_database()
        pass

    def __save_database(self):
        with open(self.__db_file_path, "w") as outfile:
            outfile.write(json.dumps(self.__DB))
