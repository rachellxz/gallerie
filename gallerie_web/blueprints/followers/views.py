from flask import Blueprint, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models.follow import Follow
from models.user import User

followers_blueprint = Blueprint("followers",
                                __name__,
                                template_folder="templates")


# follow user
@followers_blueprint.route("/create", methods=["POST"])
@login_required
def create():
    artist = User.get_or_none(User.id == request.form["artist"])
    follower = User.get_or_none(User.id == request.form["follower"])

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


# unfollow user
@followers_blueprint.route("/remove", methods=["POST"])
@login_required
def destroy():
    artist = User.get_or_none(User.id == request.form["artist"])
    follower = User.get_or_none(User.id == request.form["follower"])
    query = Follow.get_or_none(Follow.artist_id == artist.id
                               and Follow.follower_id == follower.id)
    if query.delete_instance():
        flash(f"You are no longer following {artist.username}")
        return redirect(url_for("users.show", username=artist.username))
    else:
        flash(f"Hmm, an error occurred. Please try again.")
        return redirect(url_for("users.show", username=artist.username))
