from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# Returns a datatype for table description
Base = declarative_base()


# Class describing the students table
class Students(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    year = Column(Integer)


def main():
    # Configure the engine. Connection config.
    engine = create_engine('sqlite:///school.sqlite')

    # Create the session maker, then the session. The actual connection to database
    Session = sessionmaker(bind=engine)
    session = Session()

    # Printing the menu to the user
    print('1. Read all students\n'
          '2. Get student by id\n'
          '3. Add student\n'
          '4. Edit student\n'
          '5. Remove student\n'
          '6. Search\n'
          '7. Exit\n')

    while True:

        alternative = int(input('Your entry: '))

        # 1. Read all students
        if alternative == 1:
            # Query all students using session object
            student = session.query(Students).all()

            if student:
                for stud in student:
                    print(f'id: {stud.id}, name: {stud.name}, email: {stud.email}, year: {stud.year}')

            else:
                print('No students found')

        # 2. Get student by id
        if alternative == 2:
            studid2 = int(input('Student id: '))

            find_stud = session.query(Students).get(studid2)

            if find_stud:
                print(f'id: {find_stud.id}, name: {find_stud.name}, email: {find_stud.email}, year: {find_stud.year}')

            else:
                print('Student not found')

        # 3. Add student
        if alternative == 3:

            # User input, adding new student
            name3 = input('Name: ')
            email3 = input('Email: ')
            year3 = int(input('Year: '))

            # userinput into object "new_student"
            new_student = Students(name=name3, email=email3, year=year3)

            # Add new transaction and commit student
            session.add(new_student)
            session.commit()

            # Print new student
            print(f'Added student: id: {new_student.id}, name: {new_student.name}, email: {new_student.email}, year: {new_student.year}')

        # 4. Edit student
        if alternative == 4:
            # User input, editing new student
            studid4 = input('Student id: ')
            
            name4 = input('Name: ')
            email4 = input('Email: ')
            year4 = int(input('Year: '))

            # Finding the given student by studid4
            student = session.query(Students).get(studid4)

            if student:
                # Editing content. This wil be added to transaction automatically
                student.name = name4
                student.email = email4
                student.year = year4

                # Perform all operations in the transaction
                session.commit()

                # Printing results
                print('Student was edited successfully')

            else:
                print('Student not found')

        # 5. Remove student
        if alternative == 5:
            studid5 = int(input('Student id: '))

            # Searching if student exist
            student = session.query(Students).get(studid5)

            if student:
                # Adding delete operation to transaction and perform the operation
                session.delete(student)
                session.commit()

                print('Student was removed successfully ')

            else:
                print('Student not found')

        # 6. Search
        if alternative == 6:
            search = input('Search for matching name: ')

            # Query all students with their name matching search using "like" function.
            students = session.query(Students).filter(Students.name.like(search))

            for stud in students:
                print(f'id: {stud.id}, name: {stud.name}, email: {stud.email}, year: {stud.year}')

        # Exit
        if alternative == 7:
            return


if __name__ == '__main__':
    main()