using CommunityToolkit.Mvvm.ComponentModel;

namespace The_Bibites_Game_Launcher.ViewModels;

public partial class MainViewModel : ViewModelBase
{
    [ObservableProperty]
    private string _greeting = "Welcome to The Bibites Game Launcher!\nAs you can see it is not finished yet.";
}
