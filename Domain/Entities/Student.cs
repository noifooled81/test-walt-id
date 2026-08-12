using Domain.Enums;

namespace Domain.Entities;

public sealed class Student
{
    public string FirstName { get; private set; } = null!;
    public string LastName { get; private set; } = null!;
    public DateTimeOffset Birthday { get; private set; }
    public Gender Gender { get; private set; }
    public int Intake { get; private set; }
    public string School { get; private set; } = null!;
    public string Program { get; private set; } = null!;
    public StudentStatus Status { get; private set; }

    public Student(string firstName, string lastName, DateTimeOffset birthday, Gender gender, int intake, string school, string program, StudentStatus status)
    {
        ArgumentNullException.ThrowIfNullOrWhiteSpace(firstName, nameof(firstName));
        ArgumentNullException.ThrowIfNullOrWhiteSpace(lastName, nameof(lastName));
        ArgumentOutOfRangeException.ThrowIfLessThan(intake, 2019, nameof(intake));
        ArgumentNullException.ThrowIfNullOrWhiteSpace(school, nameof(school));
        ArgumentNullException.ThrowIfNullOrWhiteSpace(program, nameof(program));

        if (!Enum.IsDefined(gender))
        {
            throw new ArgumentOutOfRangeException(nameof(gender), "Invalid gender value.");
        }

        if (!Enum.IsDefined(status))
        {
            throw new ArgumentOutOfRangeException(nameof(status), "Invalid student status value.");
        }

        FirstName = firstName;
        LastName = lastName;
        Birthday = birthday;
        Gender = gender;
        Intake = intake;
        School = school;
        Program = program;
        Status = status;
    }
}
