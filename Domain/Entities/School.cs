using System.Text.Json.Serialization;

namespace Domain.Entities;

public sealed class School
{
    public string Name { get; private set; } = null!;

    [JsonIgnore]
    public List<string> Programs { get; private set; }

    public School(string name, List<string> programs)
    {
        ArgumentNullException.ThrowIfNullOrWhiteSpace(name, nameof(name));
        ArgumentNullException.ThrowIfNull(programs, nameof(programs));

        if (programs.Any(string.IsNullOrWhiteSpace))
        {
            throw new ArgumentException("Programs list cannot contain null or empty entries.", nameof(programs));
        }

        Name = name;
        Programs = new List<string>(programs);
    }
}
