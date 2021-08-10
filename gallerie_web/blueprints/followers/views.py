from flask import Blueprint, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models.follow import Follow
from models.user import User

followers_blueprint = Blueprint("followers",
                                __name__,
                                template_folder="templates")


# follow user
@followers_blueprint.route("/", methods=["POST"])
@login_required
def create():
    artist = User.get_or_none(User.id == request.form['artist'])
    follower = User.get_or_none(User.id == current_user.id)

    if artist and follower:
        # if artist account is public:
        if artist.public_profile:
            follow = Follow(artist=artist, follower=follower, approved=True)
            if follow.save():
                flash(f"You are now following {artist.username}.")
                return redirect(url_for("users.show",
                                        username=artist.username))
            else:
                flash(
                    f"Hmm, an error seems to have occurred. Please try again.")
                return redirect(url_for("users.show",
                                        username=artist.username))
        # if artist account is private:
        else:
            follow = Follow(artist=artist, follower=follower)
            if follow.save():
                flash(
                    f"You have submitted a follow request to {artist.username}"
                )
                return redirect(url_for("users.show",
                                        username=artist.username))
            else:
                flash(
                    f"Hmm, an error seems to have occurred. Please try again.")
                return redirect(url_for("users.show",
                                        username=artist.username))
