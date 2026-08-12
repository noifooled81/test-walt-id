using Domain.Enums;

namespace Domain.Entities;

public sealed class Score
{
    public Grade Grade { get; private set; }
    public double GPA { get; private set; } // 4.0 grading scale
    public GpaDescriptor Descriptor { get; private set; }

    public Score(Grade grade)
    {
        if (!Enum.IsDefined(grade))
        {
            throw new ArgumentOutOfRangeException(nameof(grade), "Invalid grade value.");
        }

        switch (grade)
        {
            case Grade.A:
                GPA = 4.0;
                Descriptor = GpaDescriptor.Excellent;
                break;
            case Grade.B:
                GPA = 3.0;
                Descriptor = GpaDescriptor.Good;
                break;
            case Grade.C:
                GPA = 2.0;
                Descriptor = GpaDescriptor.Average;
                break;
            case Grade.D:
                GPA = 1.0;
                Descriptor = GpaDescriptor.Poor;
                break;
            case Grade.F:
                GPA = 0.0;
                Descriptor = GpaDescriptor.Fail;
                break;
            default:
                throw new ArgumentOutOfRangeException(nameof(grade), "Invalid grade value.");
        }
    }
}
