using Domain.Entities;

namespace Domain.Credentials;

public sealed class MyUniCredential
{
    public string UniName { get; } = "My Uni";
    public School School { get; private set; } = null!;
    public Student StudentInfo { get; private set; } = null!;
    public Score StudentScore { get; private set; } = null!;

    public MyUniCredential(School school, Student studentInfo, Score studentScore)
    {
        ArgumentNullException.ThrowIfNull(school, nameof(school));
        ArgumentNullException.ThrowIfNull(studentInfo, nameof(studentInfo));
        ArgumentNullException.ThrowIfNull(studentScore, nameof(studentScore));

        School = school;
        StudentInfo = studentInfo;
        StudentScore = studentScore;
    }
}
