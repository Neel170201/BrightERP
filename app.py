                if u4.button("➕ Add User", key="add_user_btn"):
                    if not new_uname.strip() or len(new_upass.strip()) < 12:
                        st.warning("Username and a password of at least 12 characters are required.")
                    else:
                        try:
                            cursor.execute(
                                "INSERT INTO users (username, password, role) VALUES (?,?,?)",
                                (new_uname.strip(), hash_pw(new_upass.strip()), new_role),
                            )
                            conn.commit()
                            st.success(f"✅ User '{new_uname.strip()}' added as {new_role}")
                            st.rerun()
                        except Exception:
                            conn.rollback()
                            st.error(f"❌ Username '{new_uname.strip()}' already exists")

                st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)
                st.markdown(_label("🗑  Delete / Reset Password", margin_bottom=10), unsafe_allow_html=True)

                d1, d2, d3, d4 = st.columns([2, 2, 1, 1])
                del_uname   = d1.text_input("USERNAME TO MANAGE", key="del_uname", placeholder="username")
                reset_upass = d2.text_input("NEW PASSWORD (for reset)", key="reset_pass", placeholder="leave blank to delete", type="password")

                d3.markdown('<div style="height:26px;"></div>', unsafe_allow_html=True)
                if d3.button("🔑 Reset PW", key="reset_pw_btn"):
                    if not del_uname.strip() or len(reset_upass.strip()) < 12:
                        st.warning("Enter username and a new password of at least 12 characters.")
                    elif del_uname.strip() == st.session_state["username"]:
                        st.warning("To change your own password, sign out and use the 'Forgot / Reset Password' option on the login screen.")
                    else:
                        cursor.execute(
                            "UPDATE users SET password=? WHERE username=?",
                            (hash_pw(reset_upass.strip()), del_uname.strip()),
                        )
                        conn.commit()
                        if cursor.rowcount:
                            st.success(f"✅ Password reset for '{del_uname.strip()}'")
                        else:
                            st.error("User not found")
                        st.rerun()

                d4.markdown('<div style="height:26px;"></div>', unsafe_allow_html=True)
                if d4.button("🗑 Delete User", key="del_user_btn"):
                    if not del_uname.strip():
                        st.warning("Enter a username to delete.")
                    elif del_uname.strip() == st.session_state["username"]:
                        st.error("❌ Cannot delete yourself.")
                    else:
                        cursor.execute("DELETE FROM users WHERE username=?", (del_uname.strip(),))
                        conn.commit()
                        if cursor.rowcount:
                            st.success(f"✅ User '{del_uname.strip()}' deleted")
                        else:
                            st.error("User not found")
                        st.rerun()

        # ── ADMIN SUB-TAB 5: SHAPE MAPPING ────────────────────────────────────
            if admin_section == '🔀 Shape Mapping':
                st.markdown(_label("🔀  Shape Alias Mapping — alias entered in Excel → saved as mapped value in DB", margin_bottom=16), unsafe_allow_html=True)

                # ── Current mappings table ─────────────────────────────────────
                maps_df = read_frame(
                    "SELECT id, alias, mapped_to FROM shape_mappings ORDER BY alias", conn
                )

                if maps_df.empty:
                    st.info("ℹ️ No mappings saved yet. Add one below.")
                else:
                    st.markdown(_label("📋  Existing Mappings", margin_bottom=6), unsafe_allow_html=True)
                    st.dataframe(
                        maps_df.rename(columns={"id": "ID", "alias": "ALIAS (Excel value)", "mapped_to": "MAPPED TO (DB value)"}),
                        use_container_width=True,
                        hide_index=True,
                    )

                st.markdown('<div style="height:18px;"></div>', unsafe_allow_html=True)

                # ── Add new mapping ────────────────────────────────────────────
                st.markdown(_label("➕  Add / Update Mapping", margin_bottom=10), unsafe_allow_html=True)
                mp1, mp2, mp3 = st.columns([2, 2, 1])
                new_alias  = mp1.text_input("ALIAS (e.g. RBC)", key="map_alias",    placeholder="Value in Excel…")
                new_mapped = mp2.text_input("MAPS TO (e.g. ROUND)", key="map_target", placeholder="Value to save in DB…")
                mp3.markdown('<div style="height:26px;"></div>', unsafe_allow_html=True)
                if mp3.button("💾 Save", key="save_mapping_btn"):
                    alias_val  = new_alias.strip().upper()
                    mapped_val = new_mapped.strip().upper()
                    if not alias_val or not mapped_val:
                        st.warning("Both Alias and Mapped To are required.")
                    else:
                        cursor.execute(
                            "INSERT INTO shape_mappings (alias, mapped_to) VALUES (?, ?) "
                            "ON CONFLICT(alias) DO UPDATE SET mapped_to=excluded.mapped_to",
                            (alias_val, mapped_val),
                        )
                        conn.commit()
                        st.success(f"✅ Mapping saved: **{alias_val}** → **{mapped_val}**")
                        st.rerun()

                st.markdown('<div style="height:18px;"></div>', unsafe_allow_html=True)

                # ── Delete mapping ─────────────────────────────────────────────
                if not maps_df.empty:
                    st.markdown(_label("🗑  Delete a Mapping", margin_bottom=10), unsafe_allow_html=True)
                    del1, del2 = st.columns([3, 1])
                    alias_to_del = del1.selectbox(
                        "Select alias to delete",
                        options=maps_df["alias"].tolist(),
                        key="del_alias_select",
                        label_visibility="collapsed",
                    )
                    del2.markdown('<div style="height:26px;"></div>', unsafe_allow_html=True)
                    if del2.button("🗑 Delete", key="del_mapping_btn"):
                        cursor.execute("DELETE FROM shape_mappings WHERE alias=?", (alias_to_del,))
                        conn.commit()
                        st.success(f"✅ Mapping '{alias_to_del}' deleted")
                        st.rerun()

        # ── CLOSE ─────────────────────────────────────────────────────────────────
        # Connection is released in the outer finally block.

finally:
    conn.close()
